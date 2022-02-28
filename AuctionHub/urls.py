from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_product", views.add_product, name="add_product"),
    path("details/<int:id>", views.details, name="details"),
    path("categories", views.categories, name="categories"),
    path("filter/<str:name>", views.filter, name="filter"),
    path("comment/<int:id>", views.comment, name="comment"),
    path("bid/<int:id>", views.bid, name="bid"),
    path("end/<int:itemId>", views.end, name="end"),
    path("all", views.all, name="all"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watch", views.watch, name="watch"),
    path("userpage", views.userpage, name="userpage"),
    path("mybids", views.mybids, name="mybids")

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
