from django.urls import path
from exploration import views

urlpatterns = [
    path('', views.render_Home, name="Home"),
    path('data', views.render_Data, name="data-home"),
    path('GetGSEData', views.GetGSEData, name="datafetch"),
    path('DeleteGSE',views.DeleteGSE,name="deleteGSE"),
    path('exploration', views.render_exploration, name = "exploration-home"),
    path('getPlotData', views.get_plot_data, name = "exploration-api"),
    path('view',views.get_GSEview,name="GSEView"),
    path('SaveGSEData',views.SaveGSEData,name="savedata"),
    path('GetDatafromDB',views.GetDatafromDB,name="getTargets")
]