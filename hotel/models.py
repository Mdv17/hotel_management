from django.db import models
from django.utils.text import slugify
from django.utils.html import mark_safe

from userauths.models import User
from shortuuid.django_fields import ShortUUIDField
import shortuuid
from django_ckeditor_5.fields import CKEditor5Field
from taggit.managers import TaggableManager

HOTEL_STATUS = (
    ("Draft", "Draft"),
    ("Disabled", "Disabled"),
    ("Rejected", "Rejected"),
    ("In Review", "In Review"),
    ("Live", "Live"),
)

ICON_TYPE = (
    ('Bootstrap Icons', 'Bootstrap Icons'),
    ('Fontawesome Icons', 'Fontawesome Icons'),
    ('Box Icons', 'Box Icons'),
    ('Remi Icons', 'Remi Icons'),
    ('Flat Icons', 'Flat Icons'),
)

PAYMENT_STATUS = (
    ("paid", "Paid"),
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("cancelled", "Cancelled"),
    ("initiated", 'Initiated'),
    ("failed", 'failed'),
    ("refunding", 'refunding'),
    ("refunded", 'refunded'),
    ("unpaid", 'unpaid'),
    ("expired", 'expired'),
)

class Hotel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = CKEditor5Field(null=True, blank=True, config_name='extends')
    image = models.FileField(upload_to="hotel_gallery")
    address = models.CharField(max_length=1000)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    status = models.CharField(max_length=20, choices=HOTEL_STATUS, default="Live")

    tags = TaggableManager(blank=True)
    views = models.IntegerField(default=0)
    featured = models.BooleanField(default=False)
    hid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    slug = models.SlugField(unique=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    # I am overriding the save method bcoz if a user saves the same name as another hotel we will get an error. So we want to fix it in the backend
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            uuid_key = shortuuid.uuid
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.name) + '-' + str(uniqueid.lower())

        super(Hotel, self).save(*args, **kwargs)

    def thumbnail(self):
        return mark_safe("<img src='%s' width='50' height='50' style='object-fit: cover; border-radius: 6px;' />" % (self.image.url))
    
    def hotel_gallery(self):
        return HotelGallery.objects.filter(hotel=self)
    
    def hotel_room_type(self):
        return RoomType.objects.filter(hotel=self)
    

class HotelGallery(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    image = models.FileField(upload_to="hotel_gallery")
    hgid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")

    def __str__(self):
        return str(self.hotel.name)
    
    class Meta:
        verbose_name_plural = 'Hotel Gallery'

class HotelFeatures(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    icon_type = models.CharField(max_length=100, null=True, blank=True, choices=ICON_TYPE)
    icon = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    hfid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")

    def __str__(self):
        return str(self.name)
    
    class Meta:
        verbose_name_plural = "Hotel Features"

class HotelFAQs(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    question = models.CharField(max_length=1000)
    answer = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    hfqid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")

    def __str__(self):
        return str(self.question)
    
    class Meta:
        verbose_name_plural = "Hotel FAQs"

class RoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    type = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    number_of_beds = models.PositiveIntegerField(default=0) # It mustnt be negative thats why
    room_capacity = models.PositiveIntegerField(default=0)
    rtid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    slug = models.SlugField(unique=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.hotel.name} - {self.price}"

    def rooms_count(self):
        return Room.objects.filter(room_type=self).count()
    
    class Meta:
        verbose_name_plural = 'Room Type'

    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.type) + "-" + str(uniqueid.lower())
            
        super(RoomType, self).save(*args, **kwargs) 


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=1000)
    is_available = models.BooleanField(default=True)
    rid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hotel.name} - {self.room_type.type} -  Room {self.room_number}"
    
    class Meta:
        verbose_name_plural = "Rooms"

    def price(self):
        return self.room_type.price
    
    def number_of_beds(self):
        return self.room_type.number_of_beds
    
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS, default="initiated")

    full_name = models.CharField(max_length=1000, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=1000, null=True, blank=True)
    
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True) # When Booking is deleted we want to keep information in the database
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True)
    room = models.ManyToManyField(Room)
    before_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_days = models.PositiveIntegerField(default=0)
    num_adults = models.PositiveIntegerField(default=1)
    num_children = models.PositiveIntegerField(default=0)
    checked_in = models.BooleanField(default=False)
    checked_out = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    checked_in_tracker = models.BooleanField(default=False, help_text="DO NOT CHECK THIS BOX")
    checked_out_tracker = models.BooleanField(default=False, help_text="DO NOT CHECK THIS BOX")
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # coupons = models.ManyToManyField("hotel.Coupon", blank=True)
    stripe_payment_intent = models.CharField(max_length=1000,null=True, blank=True)
    success_id = ShortUUIDField(length=300, max_length=505, alphabet="abcdefghijklmnopqrstuvxyz1234567890")
    booking_id = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")


    def __str__(self):
        return f"{self.booking_id}"
    
    def rooms(self):
        return self.room.all().count()
    
class ActivityLog(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    guest_out = models.DateTimeField()
    guest_in = models.DateTimeField()
    description = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.booking)
    
class StaffOnDuty(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    staff_id = models.CharField(null=True, blank=True, max_length=100)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.staff_id)
    

# class Coupon(models.Model):
#     code = models.CharField(max_length=1000)
#     type = models.CharField(max_length=100, choices=DISCOUNT_TYPE, default="Percentage")
#     discount = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(100)])
#     redemption = models.IntegerField(default=0)
#     date = models.DateTimeField(auto_now_add=True)
#     active = models.BooleanField(default=True)
#     make_public = models.BooleanField(default=False)
#     valid_from = models.DateField()
#     valid_to = models.DateField()
#     cid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")

    
#     def __str__(self):
#         return self.code
    
#     class Meta:
#         ordering =['-id']


# class CouponUsers(models.Model):
#     coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
#     booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    
#     full_name = models.CharField(max_length=1000)
#     email = models.CharField(max_length=1000)
#     mobile = models.CharField(max_length=1000)

#     def __str__(self):
#         return str(self.coupon.code)
    
#     class Meta:
#         ordering =['-id']


# class RoomServices(models.Model):
#     booking = models.ForeignKey(Booking, null=True, on_delete=models.CASCADE)
#     room = models.ForeignKey(Room, on_delete=models.CASCADE)
#     date = models.DateField(auto_now_add=True)
#     service_type = models.CharField(max_length=20, choices=SERVICES_TYPES)
#     price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)

#     def str(self):
#         return str(self.booking) + " " + str(self.room) + " " + str(self.service_type)

# class Notification(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
#     booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
#     type = models.CharField(max_length=100, default="new_order", choices=NOTIFICATION_TYPE)
#     seen = models.BooleanField(default=False)
#     nid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
#     date= models.DateField(auto_now_add=True)
    
#     def __str__(self):
#         return str(self.user.username)
    
#     class Meta:
#         ordering = ['-date']

