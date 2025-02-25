from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, F, Sum, Value
from django.db.models.functions import Coalesce
from django.core.mail import send_mail
from django.conf import settings

from .models import Driver, Trip, SharePart


# ============================================================
# Authentication Views
# ============================================================

def Login(request):
    """
    Handle user login.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("ride_system:HomePage")
        else:
            return HttpResponse("Invalid username or password", status=400)
    return render(request, "ride_system/login.html")


def logout_view(request):
    """
    Log out the current user.
    """
    logout(request)
    return redirect("ride_system:Login")


def CreateNewAccount(request):
    """
    Create a new user account and log the user in.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")

        if User.objects.filter(username=username).exists():
            return HttpResponse("Username already exists", status=400)

        new_account = User.objects.create_user(username=username, password=password, email=email)
        login(request, new_account)
        return redirect("ride_system:HomePage")
    return render(request, "ride_system/createnewaccount.html")


@login_required
def HomePage(request):
    """
    Render the homepage for authenticated users.
    """
    return render(request, "ride_system/homepage.html")


# ============================================================
# Driver Views
# ============================================================

@login_required
def DriverReg(request):
    """
    Register or update the driver's profile.
    """
    if request.method == "POST":
        drivername = request.POST.get("drivername")
        car_type = request.POST.get("car_type")
        plate_number = request.POST.get("plate_number")
        capacity = request.POST.get("capacity")
        special = request.POST.get("special")

        driver, created = Driver.objects.get_or_create(
            account=request.user,
            defaults={
                'drivername': drivername,
                'car_type': car_type,
                'plate_number': plate_number,
                'capacity': int(capacity),
                'special': special,
            }
        )
        if not created:
            # Update existing driver information.
            driver.drivername = drivername
            driver.car_type = car_type
            driver.plate_number = plate_number
            driver.capacity = int(capacity)
            driver.special = special
            driver.save()
        return redirect("ride_system:MyOrders")
    else:
        try:
            driver = Driver.objects.get(account=request.user)
        except Driver.DoesNotExist:
            driver = None
        return render(request, "ride_system/driverregistration.html", {"driver": driver})


@login_required
def DriverSearch(request):
    """
    Search for trips that match the driver's vehicle type, specialty, and capacity constraints.
    """
    driver = Driver.objects.get(account=request.user)
    trips = Trip.objects.filter(
        isConfirmed=False,
        isComplete=False,
        car_type=driver.car_type,
        special=driver.special
    )
    # Annotate trips with the total number of shared passengers.
    trips = trips.annotate(
        shares_total=Coalesce(Sum('shareSet__number'), Value(0))
    ).annotate(
        total_passengers=F('number') + F('shares_total')
    ).filter(total_passengers__lte=driver.capacity)

    context = {
        'trips': trips,
    }
    return render(request, 'ride_system/driversearch.html', context)


@login_required
def MyOrders(request):
    """
    Display confirmed trips (orders) for the driver.
    """
    driver = Driver.objects.get(account=request.user)
    confirmed_trips = Trip.objects.filter(isConfirmed=True, isComplete=False, driver=driver)
    context = {
        "confirmed_trips": confirmed_trips
    }
    return render(request, "ride_system/myorders.html", context)


@login_required
def TripSelect(request, trip_id):
    """
    Confirm a trip for the driver and send an email notification to every participant in the shareSet.
    """
    driver = Driver.objects.get(account=request.user)
    trip = get_object_or_404(Trip, id=trip_id)
    if request.method == "POST":
        trip.isConfirmed = True
        trip.driver = driver
        trip.save()

        # Prepare email content.
        subject = "Your Trip Has Been Confirmed"
        message = (
            f"Dear Participant,\n\n"
            f"The trip to {trip.destination} on {trip.date} has been confirmed by driver {driver.drivername}.\n"
            "Thank you for using our service!"
        )

        # Create a recipient list from each SharePart in the shareSet.
        recipient_list = [share.account.email for share in trip.shareSet.all() if share.account.email]
        recipient_list.append(trip.owner.email)
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )
    return redirect("ride_system:MyOrders")



@login_required
def TripComplete(request, trip_id):
    """
    Mark a trip as complete.
    """
    trip = get_object_or_404(Trip, id=trip_id)
    if request.method == "POST":
        trip.isComplete = True
        trip.save()
    return redirect("ride_system:MyOrders")


# ============================================================
# Trip Views
# ============================================================

@login_required
def Request(request):
    """
    Create a new trip request.
    """
    if request.method == "POST":
        destination = request.POST.get("destination")
        date = request.POST.get("date")
        number = request.POST.get("number")
        car_type = request.POST.get("car_type")
        special = request.POST.get("special")
        isShared = request.POST.get("isShared") == "on"

        trip = Trip.objects.create(
            owner=request.user,
            destination=destination,
            date=date,
            number=int(number),
            car_type=car_type,
            special=special,
            isShared=isShared
        )
        trip.save()
        return redirect("ride_system:MyTrips")
    return render(request, "ride_system/request.html")


@login_required
def MyTrips(request):
    """
    Display trips created by the user, trips the user has joined, and confirmed trips.
    """
    owned_trips = Trip.objects.filter(owner=request.user, isConfirmed=False, isComplete=False)
    shared_trips = Trip.objects.filter(shareSet__account=request.user, isConfirmed=False, isComplete=False)
    confirmed_trips = Trip.objects.filter(
        Q(owner=request.user) | Q(shareSet__account=request.user),
        isConfirmed=True,
        isComplete=False
    )

    context = {
        "owned_trips": owned_trips,
        "shared_trips": shared_trips,
        "confirmed_trips": confirmed_trips
    }
    return render(request, "ride_system/mytrips.html", context)


@login_required
def TripEdit(request, trip_id):
    """
    Edit the details of a trip.
    """
    trip = get_object_or_404(Trip, id=trip_id)
    if request.method == "POST":
        trip.destination = request.POST.get("destination")
        trip.date = request.POST.get("date")
        trip.number = int(request.POST.get("number"))
        trip.car_type = request.POST.get("car_type")
        trip.special = request.POST.get("special")
        trip.isShared = request.POST.get("isShared") == "on"
        if not trip.isShared:
            # If the trip is not shared, clear all shared associations.
            trip.shareSet.clear()
        trip.save()
        return redirect("ride_system:MyTrips")
    return render(request, "ride_system/tripedit.html", {"trip": trip})


@login_required
def TripExit(request, trip_id):
    """
    Allow the user to exit a shared trip.
    """
    trip = get_object_or_404(Trip, id=trip_id)
    if request.method == "POST":
        share_instance = trip.shareSet.filter(account=request.user).first()
        if share_instance:
            trip.shareSet.remove(share_instance)
            share_instance.delete()
    return redirect("ride_system:MyTrips")


@login_required
def SearchShare(request):
    """
    Search for shared trips based on destination, date range, and passenger count.
    """
    destination_query = request.GET.get('destination', '')
    arrival_from = request.GET.get('arrival_from', '')
    arrival_to = request.GET.get('arrival_to', '')
    passengers = request.GET.get('passengers', '')

    rides = Trip.objects.filter(isConfirmed=False, isComplete=False, isShared=True)
    if destination_query:
        rides = rides.filter(destination__icontains=destination_query)
    if arrival_from:
        rides = rides.filter(date__gte=arrival_from)
    if arrival_to:
        rides = rides.filter(date__lte=arrival_to)
    rides = rides.exclude(shareSet__account=request.user)

    context = {
        'rides': rides,
        'destination_query': destination_query,
        'arrival_from': arrival_from,
        'arrival_to': arrival_to,
        'passengers': passengers,
    }
    return render(request, 'ride_system/searchshare.html', context)


@login_required
def TripJoin(request, trip_id):
    """
    Allow a user to join a shared trip.
    """
    trip = get_object_or_404(Trip, id=trip_id)
    if request.method == "POST":
        join_number = request.POST.get("join_number", ' ')
        try:
            join_number = int(join_number)
        except ValueError:
            join_number = 1
        share_instance = SharePart.objects.create(account=request.user, number=join_number)
        trip.shareSet.add(share_instance)
        return redirect("ride_system:MyTrips")
    return redirect("ride_system:SearchShare")
