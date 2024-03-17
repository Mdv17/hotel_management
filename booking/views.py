from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse

from django.views.decorators.csrf import csrf_exempt

from hotel.models import Hotel, Room, Booking, HotelGallery, HotelFeatures, HotelFAQs, RoomType, ActivityLog, StaffOnDuty

@csrf_exempt
def check_room_availability(request):
    if request.method == "POST":
        id = request.POST.get("hotel-id")
        checkin = request.POST.get("checkin")
        checkout = request.POST.get("checkout")
        adult = request.POST.get("adult")
        children = request.POST.get("children")
        room_type = request.POST.get("room_type")

        hotel = Hotel.objects.get(id=id)
        room_type = RoomType.objects.get(hotel=hotel, slug=room_type)

        print("id ====", id)
        print("room_type ====", room_type)
        print("checkin ====", checkin)
        print("checkout ====", checkout)
        print("adult ====", adult)
        print("children ====", children)

        url = reverse("hotel:room_type_detail", args=[hotel.slug, room_type.slug])
        url_with_params = f"{url}?hotel-id={id}&checkin={checkin}&checkout={checkout}&adult={adult}&children={children}&room_type={room_type}"
        return HttpResponseRedirect(url_with_params)
    
def add_to_selection(request):
    room_selection = {}

    # Get values or default to empty string if not provided
    adult = request.GET.get('adult', '')
    children = request.GET.get('children', '')

    room_selection[str(request.GET['id'])] = {
        'hotel_id': request.GET['hotel_id'],
        'hotel_name': request.GET['hotel_name'],
        'room_name': request.GET['room_name'],
        'room_price': request.GET['room_price'],
        'number_of_beds': request.GET['number_of_beds'],
        'room_number': request.GET['room_number'],
        'room_type': request.GET['room_type'],
        'room_id': request.GET['room_id'],
        'checkin': request.GET['checkin'],
        'checkout': request.GET['checkout'],
        'adult': adult if adult.isdigit() else '0',  # Default to '0' if not a digit
        'children': children if children.isdigit() else '0',  # Default to '0' if not a digit
    }

    if 'selection_data_obj' in request.session:
        selection_data = request.session['selection_data_obj']
        if str(request.GET['id']) in selection_data:
            # Convert to int and update the session
            selection_data[str(request.GET['id'])]['adult'] = int(room_selection[str(request.GET['id'])]['adult'])
            selection_data[str(request.GET['id'])]['children'] = int(room_selection[str(request.GET['id'])]['children'])
        else:
            # Update the session with new selection
            selection_data.update(room_selection)

        request.session['selection_data_obj'] = selection_data
    else:
        # Create a new session object if it doesn't exist
        request.session['selection_data_obj'] = room_selection

    data = {
        "data": request.session['selection_data_obj'],
        'total_selected_items': len(request.session['selection_data_obj'])
    }

    return JsonResponse(data)


