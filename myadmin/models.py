from django.db import models
import uuid

from django.db import models


# Create your models here.

class User(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('shelter', 'Shelter'),
        ('admin', 'Admin'),
    ]
    user_id  = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email    = models.CharField(max_length=50)
    contact  = models.BigIntegerField(blank=True, null=True)   # ✅ nullable
    address  = models.CharField(max_length=100, blank=True, null=True)  # ✅ nullable
    username = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=128)
    role     = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    class Meta:
        db_table = 'user_happypaws'
        managed = False

    def __str__(self):
        return self.username or self.email


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column='user_id'  
    )

    ratings = models.IntegerField()
    comments = models.TextField()
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'feedback'
        managed = False   

    def __str__(self):
        return f"Feedback {self.feedback_id}"

class Shelter(models.Model):
    shelter_id = models.AutoField(primary_key=True)
    shelter_name = models.CharField(max_length=50)
    user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    db_column='user_id',
    null=True,
    blank=True
)

    address1 = models.CharField(max_length=255, null=True, blank=True)
    address2 = models.CharField(max_length=255, null=True, blank=True)
    landmark = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    contact = models.BigIntegerField()
    capacity = models.IntegerField()
    available_slot_count = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True 
        db_table = 'shelter'

    def __str__(self):
        return self.shelter_name



class Product_form(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    age_range = models.CharField(max_length=50)
    product_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_form'

    def __str__(self):
        return self.product_name


class Order_table(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        db_column='user_id',     # exact column name in order_table
        on_delete=models.DO_NOTHING
    )
    product = models.ForeignKey(
        Product_form,
        db_column='product_id',
        on_delete=models.DO_NOTHING
    )
    TotalAmount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField()
    payment_status = models.CharField(max_length=50)
    payment_mode = models.CharField(max_length=50)
    payment_date = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'order_table'   
        managed = False            

    def __str__(self):
        return f"Order {self.order_id} by User {self.user_id}"



class Pet(models.Model):
    pet_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='pets'
    )

    pet_name = models.CharField(max_length=30)
    breed = models.CharField(max_length=20)
    age = models.IntegerField()
    weight = models.DecimalField(max_digits=4, decimal_places=1)

    gender = models.CharField(
        max_length=6,
        choices=[('female', 'Female'), ('male', 'Male')]
    )

    pet_image = models.ImageField(upload_to='pets/',blank=True)


    class Meta:
        db_table = 'pet'   
        managed = False 

    def __str__(self):
        return self.pet_name


class PetHealth(models.Model):
    pet_health_id = models.AutoField(primary_key=True)

    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        db_column='pet_id',
        related_name='health_records'
    )

    disease = models.CharField(max_length=30, null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    medicine = models.CharField(max_length=50, null=True, blank=True)
    last_vaccination = models.DateField(null=True, blank=True)
    next_vaccination = models.DateField(null=True, blank=True)
    vaccine_name = models.CharField(max_length=50, null=True, blank=True)

    reminder_status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('sent', 'Sent')],
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'pet_health'   
        managed = False 

    def __str__(self):
        return f"{self.pet.pet_name} - Health Record"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.email)


class BoardingRequest(models.Model):
    request_id = models.AutoField(primary_key=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    start_date = models.DateField()
    end_date = models.DateField()

    boarding_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'boarding_request'   
        managed = False 

    def __str__(self):
        return f"{self.pet} booking at {self.shelter}"


class ShelterPayment(models.Model):
    shelter_payment_id = models.AutoField(primary_key=True)

    request = models.ForeignKey(
        BoardingRequest,
        on_delete=models.CASCADE,
        db_column='request_id'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id'
    )

    shelter = models.ForeignKey(
        Shelter,
        on_delete=models.CASCADE,
        db_column='shelter_id'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('online', 'Online'),
    ]
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODE_CHOICES)

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES)

    payment_date = models.DateTimeField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shelter_payment'
        managed = False  # keep False since table already exists

    def __str__(self):
        return f"Payment {self.shelter_payment_id}"












# models.py

from django.db import models
from .models import User, Product_form   # your existing models


class Order_table(models.Model):
    order_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        User,
        db_column='user_id',
        on_delete=models.DO_NOTHING
    )

    product = models.ForeignKey(
        Product_form,
        db_column='product_id',
        on_delete=models.DO_NOTHING
    )

    TotalAmount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField()

    payment_status = models.CharField(max_length=20)
    payment_mode = models.CharField(max_length=20)

    payment_id = models.CharField(max_length=100, null=True, blank=True)
    
    payment_date = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'order_table'
        managed = False

    def __str__(self):
        return f"Order {self.order_id}"


class Order_item(models.Model):
    order_item_id = models.AutoField(primary_key=True)

    order = models.ForeignKey(
        Order_table,
        db_column='order_id',
        on_delete=models.DO_NOTHING
    )

    product = models.ForeignKey(
        Product_form,
        db_column='product_id',
        on_delete=models.DO_NOTHING
    )

    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'order_item'
        managed = False

    def __str__(self):
        return f"Item {self.order_item_id}"


class ChatHistory(models.Model):
    chat_id = models.AutoField(primary_key=True)
    
    # Link to your existing User model
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        db_column='user_id',
        related_name='chat_history'
    )
    
    user_query = models.TextField()
    ai_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_history'
        managed = True  # Set to True so Django creates the table for you

    def __str__(self):
        return f"Chat by {self.user.username} at {self.timestamp}"