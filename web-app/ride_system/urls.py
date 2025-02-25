from django.urls import path
from . import views

app_name = "ride_system"
urlpatterns = [
    path("", views.Login, name="Login"),
    path("createnewaccount/", views.CreateNewAccount, name="CreateNewAccount"),
    path("home/", views.HomePage, name="HomePage"),
    path("logout/", views.logout_view, name="Logout"), 
    path("request/", views.Request, name="Request"),
    path("mytrips/", views.MyTrips, name="MyTrips"),
    path("driver/", views.DriverReg, name="DriverRegistration"),
    path("searchshare/", views.SearchShare, name="SearchShare"),
    path("tripedit/<int:trip_id>/", views.TripEdit, name="TripEdit"),
    path("tripexit/<int:trip_id>/", views.TripExit, name="TripExit"),
    path("tripjoin/<int:trip_id>/", views.TripJoin, name="TripJoin"),
    path("myorders/", views.MyOrders, name="MyOrders"),
    path("driversearch/", views.DriverSearch, name="DriverSearch"),
    path("tripselect/<int:trip_id>/", views.TripSelect, name="TripSelect"),
    path("tripcomplete/<int:trip_id>/", views.TripComplete, name="TripComplete")
]