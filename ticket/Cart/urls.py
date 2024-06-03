from django.urls import path
from .viewsCart import cart_view, cart_add, cart_delete, cart_update, process_checkout, checkout_success

urlpatterns = [
    path("", cart_view, name="cart_view"),
    path("add/<int:event_id>/", cart_add, name="cart_add"),
    path("update/<int:event_id>", cart_update, name="cart_update"),
    path("delete/<int:event_id>/", cart_delete, name="cart_delete"),
    path("process_checkout/", process_checkout, name="process_checkout"),
    path("checkout_success/", checkout_success, name="checkout_success"),
]
