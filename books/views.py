from django.http import FileResponse, Http404
from .serializers import *
from accounts.utils import unhash_token
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, AuthenticationFailed
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from accounts.models import User
from rest_framework.views import APIView






class APIListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100





class BookListAPIView(generics.ListAPIView):
    serializer_class = BookUseSerializer
    pagination_class = APIListPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Book.objects.all().order_by('-created_at')

    def list(self, request, *args, **kwargs):
        decoded_token = None
        user_id = None

        if request.headers.get("Authorization"):
            try:
                decoded_token = unhash_token(request.headers)
                user_id = decoded_token.get('user_id')
            except AuthenticationFailed:
                pass  # handle if needed

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data

            for book in data:
                book_obj = Book.objects.get(id=book['id'])
                # book['is_authored'] = book_obj.author.id == user_id if user_id else False
                if user_id:
                    book['is_in_cart'] = Cart.objects.filter(user_id=user_id, book_id=book['id']).exists()
                else:
                    book.pop('is_in_cart', None)  # Remove 'is_in_cart' for unauthenticated users

            return self.get_paginated_response(data)

        # serializer = self.get_serializer(queryset, many=True)
        # data = serializer.data
        #
        # for book in data:
        #     book_obj = Book.objects.get(id=book['id'])
        #     # book['is_authored'] = book_obj.author.id == user_id if user_id else False
        #     if user_id:
        #         book['is_in_cart'] = Cart.objects.filter(user_id=user_id, book_id=book['id']).exists()
        #     else:
        #         book.pop('is_in_cart', None)  # Remove 'is_in_cart' for unauthenticated users
        #
        # return Response(data)


class BookDetailAPIView(generics.RetrieveAPIView):
    serializer_class = BookBaseSerializer
    queryset = Book.objects.all()
    permission_classes = [permissions.AllowAny]  # Allow any user to access, but restrict data based on authentication

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views += 1
        instance.save()

        user_authenticated = request.user.is_authenticated

        if user_authenticated:
            decoded_token = unhash_token(request.headers)
            user_id = decoded_token.get('user_id')

            if not user_id:
                raise AuthenticationFailed("User ID not found in token")

            is_in_cart = Cart.objects.filter(user_id=user_id, book_id=instance.id).exists()
        else:
            is_in_cart = False

        # Use the appropriate serializer based on the authentication status
        serializer = self.get_serializer(instance)
        data = serializer.data

        if not user_authenticated:
            restricted_fields = ['location', 'uploaded_by', 'pdf', "is_in_cart"]
            for field in restricted_fields:
                data.pop(field, None)

        else:
            data['is_in_cart'] = is_in_cart

        return Response(data)











class CreateBookAPIView(generics.CreateAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()





class UpdateBookAPIView(generics.UpdateAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Book.objects.all()

    def perform_update(self, serializer):
        serializer.save()





class DeleteBookAPIView(generics.DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookBaseSerializer
    permission_classes = [IsAdminUser]

    def perform_destroy(self, instance):
        instance.delete()




class BookGenreList(generics.ListAPIView):
    serializer_class = TypeSerializer
    queryset = Type.objects.all()
    pagination_class = APIListPagination






class BookAuthorList(generics.ListAPIView):
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()
    pagination_class = APIListPagination





class BookGenreSearch(generics.ListAPIView):
    serializer_class = BookUseSerializer
    queryset = Book.objects.all()
    pagination_class = APIListPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='name',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,  # Set required to True
                description='Name of the genre'
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        name = self.request.query_params.get("name", None)
        if name:
            query = self.queryset.filter(genre__name=name)
        else:
            query = self.queryset.none()
        return query







class BookAuthorSearch(generics.ListAPIView):
    serializer_class = BookUseSerializer
    queryset = Book.objects.all()
    pagination_class = APIListPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='name',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='Name of the author'
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        name = self.request.query_params.get("name", None)
        if name:
            query = self.queryset.filter(author__name=name)
        else:
            query = self.queryset.none()
        return query









class SearchByNameAPIView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookUseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['title']




@method_decorator(csrf_exempt, name='dispatch')
class BookDownloadView(generics.GenericAPIView):
    queryset = Book.objects.all()
    serializer_class = BookBaseSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        decoded_token = unhash_token(request.headers)
        user_id = decoded_token.get('user_id')
        book = self.get_object()
        book.downloads += 1
        book.save()

        if book.pdf:
            try:
                response = FileResponse(book.pdf.open('rb'), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{book.pdf.name}"'
                return response
            except FileNotFoundError:
                raise Http404("File not found")
        else:
            raise Http404("PDF file not available for this book")





class RecommendedBooksView(generics.ListAPIView):
    serializer_class = BookUseSerializer
    pagination_class = APIListPagination

    def get_queryset(self):
        return Book.objects.all().order_by('-views', '-downloads')[:10]

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)









class UserCartView(generics.ListAPIView):
    serializer_class = CartUseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = APIListPagination

    def get_queryset(self):
        decoded_token = unhash_token(self.request.headers)
        user_id = decoded_token['user_id']
        queryset = Cart.objects.filter(user__id=user_id).order_by('-added_at')

        # if not queryset.exists():
        #     raise NotFound('Cart not found for this user')

        return queryset








class AddToCardView(generics.CreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        book_id = request.data.get('book')

        book = get_object_or_404(Book, id=book_id)

        if not book:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        if not Cart.objects.filter(book=book, user=user).exists():
            cart = Cart.objects.create(user=user, book=book)
        else:
            return Response({"error": "Book already in cart"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)









class RemoveFromCartView(generics.DestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        decoded_token = unhash_token(request.headers)
        user_id = decoded_token.get('user_id')
        book_id = self.kwargs.get('pk')
        print(book_id)
        try:
            cart_item = Cart.objects.get(user__id=user_id, book__id=book_id)
        except Cart.DoesNotExist:
            raise NotFound("Book not found in cart")

        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckBookInCartView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookInCartCheckSerializer
    @swagger_auto_schema(
        request_body= BookInCartCheckSerializer
    )
    def post(self, request, *args, **kwargs):
        serializer = BookInCartCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        decoded_token = unhash_token(request.headers)
        user_id = decoded_token.get('user_id')
        book_id = serializer.validated_data['book_id']

        user = get_object_or_404(User, id=user_id)
        book = get_object_or_404(Book, id=book_id)

        is_in_cart = Cart.objects.filter(user=user, book=book).exists()

        return Response(is_in_cart, status=status.HTTP_200_OK)

        # if Cart.objects.filter(user=user, book=book).exists():
        #     return Response({"message": "Book is in cart"}, status=status.HTTP_200_OK)
        # else:
        #     return Response({"message": "Book is not in cart"}, status=status.HTTP_200_OK)

