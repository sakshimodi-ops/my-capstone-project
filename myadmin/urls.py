"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from myadmin import views
from myadmin.views import chat_with_dog_ai
from rest_framework.routers import DefaultRouter
from myadmin.views import (
    UserViewSet,
    FeedbackViewSet,
    ShelterViewSet,
    ProductViewSet,
    OrderViewSet,
    PetViewSet,
    PetHealthViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'feedback', FeedbackViewSet)
router.register(r'shelters', ShelterViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'pets', PetViewSet)
router.register(r'pet-health', PetHealthViewSet)


urlpatterns = [
  
  path('index', views.index, name='index'), 
  path('signup/', views.signup),
  path('login/', views.login),  
  path('my-pets/<int:user_id>/', views.get_user_pets),
  path('add-pet-health/', views.add_pet_health),
  path('add-pet/', views.add_pet),
  path("forgot-password/", views.forgot_password),
  path("reset-password/", views.reset_password),
  path("book-shelter/", views.book_shelter),
  path("user-notifications/<int:user_id>/", views.user_notifications),
  path("make-pay/", views.make_payment),
  path('create-order/', views.create_order),
  path('orders/<int:user_id>/', views.get_user_orders),
  path('dog-chat/', views.chat_with_dog_ai),
  path('get-chat-history/<int:user_id>/', views.get_chat_history),
  path('check-email/', views.check_email),
  path('check-username/', views.check_username),
  path('auth/google/', views.google_auth),


  path('user', views.user, name='user'),
  path('feedback', views.feedback, name='feedback'),
  path('shelter', views.shelter, name='shelter'),
  path('demo', views.demo, name='demo'),
  path('layout', views.layout, name='layout'),
  path('product_form', views.product_form, name='product_form'),
  path('add_product', views.add_product, name='add_product'),
  path('view_product', views.view_product, name='view_product'),
  path('order_table', views.order_table, name='order_table'),
  path('view_pet/<int:id>', views.view_pet, name='view_pet'),  
  path('product_edit/<int:id>/', views.product_edit, name='product_edit'),
  path('product_update/<int:id>/', views.product_update, name='product_update'),
  path('product_delete/<int:id>/', views.product_delete, name='product_delete'),
  path('product_details/<int:id>/', views.product_details, name='product_details'),

  path('add_shelter', views.add_shelter, name='add_shelter'),
  path('login_screen', views.login_screen, name='login_screen'),
  path('user-pets/<int:user_id>/', views.user_pets),
  path('cancel-booking/<int:booking_id>/', views.cancel_booking),

  path('shelter_edit/<int:id>/', views.shelter_edit, name='shelter_edit'),
  path('shelter_update/<int:id>/', views.shelter_update, name='shelter_update'),
  path('shelter_delete/<int:id>/', views.shelter_delete, name='shelter_delete'),

  path('create-shelter/', views.create_shelter),
  path('shelter-requests/<int:shelter_id>/', views.get_shelter_requests),
  path('update-request-status/', views.update_request_status),
  path('shelter-payments/', views.shelter_payments, name='shelter_payments'),
  path('update-shelter/<int:shelter_id>/', views.update_shelter_profile),
  path('shelter-profile/<int:shelter_id>/', views.get_shelter_profile),
  path('shelter-earnings-dashboard/<int:shelter_id>/',views.shelter_earnings_dashboard),
  path('current-shelter-pets/<int:shelter_id>/pets/',views.current_shelter_pets),


  path('', include(router.urls)),


]



