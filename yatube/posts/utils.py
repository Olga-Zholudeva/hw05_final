from django.core.paginator import Paginator
from django.conf import settings


def paginator_func(page_list, request):
    paginator = Paginator(page_list, settings.LIMIT_POSTS)
    page_namber = request.GET.get('page')
    page_obj = paginator.get_page(page_namber)
    return page_obj
