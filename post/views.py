from rest_framework import generics, status

from post.models import Post
from post.serializers import PostSerializer
from rest_framework.response import Response

from confessionbackend.paginationsettings import PaginationSettings

from rest_framework_simplejwt.authentication import JWTAuthentication

class PostList(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    pagination_class = PaginationSettings

    def get_queryset(self):
        approved = self.request.GET.get('approved', None)
        category = self.request.GET.get('category', None)
        search = self.request.GET.get('search', None)
        order_by = self.request.GET.get('order_by', None)
        current_queryset = Post.objects.all()
        if approved is not None:
            current_queryset = current_queryset.filter(approved=approved)
        if category is not None:
            current_queryset = current_queryset.filter(category__in=[category])
        if search is not None:
            current_queryset = current_queryset.filter(text__icontains=search)
        if order_by:
            if order_by == 'popular':
                current_queryset = current_queryset.order_by('-time_created', '-likes')
            else:
                current_queryset = current_queryset.order_by(order_by)
        else:
            current_queryset = current_queryset.order_by('-id') # sort by latest by default
        return current_queryset
    
    def create(self, request, *args, **kwargs):
        if 'approved' in self.request.data:
            return Response({'message': 'Object should not contain approved flag.'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        post_id = kwargs['pk']
        current_queryset = self.get_queryset().filter(approved=True)
        prev_instance = current_queryset.filter(id__lt=post_id).order_by('-id').first()
        next_instance = current_queryset.filter(id__gt=post_id).order_by('id').first()

        prev_id = prev_instance.id if prev_instance else -1
        next_id = next_instance.id if next_instance else -1
        return Response({"data": serializer.data, "prev_id": prev_id, "next_id": next_id})
    
    def update(self, request, *args, **kwargs):
        if self.request.method == 'PUT':
            return Response({'message': "METHOD NOT ALLOWED"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        if self.request.method == 'PATCH':
            body = self.request.data
            if 'approved' in body and not JWTAuthentication().authenticate(self.request):
                return Response({'message': 'ILLEGAL OPERATION'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        if not JWTAuthentication().authenticate(self.request):
            return Response({'message': 'ILLEGAL OPERATION'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().destroy(request, *args, **kwargs)