from django.urls import path
from . import views as v
urlpatterns = [
    path("", v.home, name="home"), path("about/", v.about, name="about"),
    path("pay/", v.pay), path("check/<uuid:ref>/", v.check), path("hook/", v.hook),
    path("find/", v.find), path("album/<uuid:token>/", v.album, name="album"),
    path("album/<uuid:token>/<int:tid>/", v.fetch, name="fetch"), path("listen/<int:tid>/", v.listen),
    path("dashboard/", v.dashboard, name="dashboard"), path("dashboard.csv", v.dashboard_csv),
]
