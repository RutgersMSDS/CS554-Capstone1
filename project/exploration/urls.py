from django.urls import path
from exploration import views

urlpatterns = [
    # Login home page path
    path('', views.render_Home, name="Home"),

    # Data preparation paths
    path('data', views.render_Data, name="data-home"),
    path('GetGSEData', views.GetGSEData, name="datafetch"),
    path('DeleteGSE', views.DeleteGSE, name="deleteGSE"),

    # Data Exploration paths
    path('exploration', views.render_exploration, name="exploration-home"),
    path('getPlotData', views.get_plot_data, name="exploration-api"),
    path('view', views.get_GSEview, name="GSEView"),
    path('SaveGSEData', views.SaveGSEData, name="savedata"),
    path('GetDatafromDB', views.GetDatafromDB, name="getTargets"),

    # Data Modeling paths
    path('modeling', views.render_modeling, name='modeling-home'),
    path('dynamic_dropdown', views.dynamic_dropdown, name='values'),
    path('get_model_params', views.get_model_params, name='model_gen'),
    path('reg_model_params', views.reg_model_params, name='reg_model_gen'),

    # Data Evaluation paths
    path('evaluation', views.render_evaluation)
]
