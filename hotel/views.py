from django.shortcuts import render, redirect

from hotel.models import Hotel, Room, Booking, HotelGallery, HotelFeatures, HotelFAQs, RoomType, ActivityLog, StaffOnDuty
from django.contrib import messages

from datetime import datetime

# Create your views here.
def index(request):
    hotels = Hotel.objects.filter(status="Live") # Means only Hotels that are live 
    context = {
        "hotels": hotels
    }
    return render(request, "hotel/hotel.html", context)

def hotel_detail(request, slug):
    hotel = Hotel.objects.get(status="Live", slug=slug) #When you want to retrieve 1 item you use get but when you want to retrieve a list you use filter or all
    context = {
        "hotel":hotel,
    }

    return render(request, "hotel/hotel_detail.html", context)

def room_type_detail(request, slug, rt_slug):
    hotel = Hotel.objects.get(status="Live", slug=slug)
    room_type = RoomType.objects.get(hotel=hotel, slug=rt_slug)
    rooms = Room.objects.filter(room_type=room_type, is_available=True)

    context = {
        "hotel": hotel,
        "room_type": room_type,
        "rooms": rooms,
    }

    return render(request, "hotel/room_type_detail.html", context)

def selected_rooms(request):
    total_count = 0
    room_count = 0
    total_days = 0
    adult = 0
    children = 0
    checkin = ''
    checkout = ''

    # Check if 'selection_data_obj' is in session
    if 'selection_data_obj' in request.session:
        for h_id, item in request.session["selection_data_obj"].items():
            # Extract data from session
            id = int(item['hotel_id'])
            hotel_id = int(item['hotel_id'])
            checkin = item['checkin']
            checkout = item['checkout']
            adult = item["adult"]
            children = item["children"]
            room_type_ = item["room_type"]
            room_id = int(item["room_id"])

            room_type = RoomType.objects.get(id=room_type_)

            # Validate and parse dates
            date_format = "%Y-%m-%d"
            try:
                checkin_date = datetime.strptime(checkin, date_format) if checkin else None
                checkout_date = datetime.strptime(checkout, date_format) if checkout else None
            except ValueError as e:
                # Log the error and set dates to None or default values
                print(f"Error parsing date: {e}")
                checkin_date = checkout_date = None

            # Calculate total_days if both dates are valid
            if checkin_date and checkout_date:
                time_difference = checkout_date - checkin_date
                total_days = time_difference.days

            print("total_days=======", total_days)

    else:
        # Warn user and redirect if no selection data
        messages.warning(request, "No rooms in selection")
        return redirect("/")

    # Render the selected rooms page
    return render(request, "hotel/selected_rooms.html")
