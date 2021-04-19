from django.urls import path
from exploration import views

urlpatterns = [
    path('', views.render_exploration, name = "exploration-home"),
    path('getPlotData', views.get_plot_data, name = "exploration-api")
]