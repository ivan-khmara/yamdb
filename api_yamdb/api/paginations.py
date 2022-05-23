from rest_framework.pagination import PageNumberPagination


class ReviewsSetPagination(PageNumberPagination):
    page_size = 5


class CommentsSetPagination(PageNumberPagination):
    page_size = 5
