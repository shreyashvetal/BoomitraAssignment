from django.shortcuts import render
import os
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Polygon
import geopandas as gpd
import rasterio
import rioxarray
import numpy as np
import matplotlib.pyplot as plt



@api_view(['POST'])
def add_polygon(request):
    if request.method == 'POST':
        name = request.data.get('name')
        geojson = request.data.get('geojson')

        if not name or not geojson:
            return Response({'error': 'Both name and geojson are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            polygon = Polygon(name=name, geojson=geojson)
            polygon.save()

            return Response({'polygon_id': polygon.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Failed to create the polygon: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def calculate_ndvi(request, polygon_id):
    # Retrieve the polygon from the database
    try:
        polygon = Polygon.objects.get(id=polygon_id)
    except Polygon.DoesNotExist:
        return Response({'error': 'Polygon not found'}, status=status.HTTP_404_NOT_FOUND)

    geojson_data = polygon.geojson

    # Open Sentinel 2 imagery from AWS
    sentinel_path = "s3://sentinel-cogs/sentinel-s2-l2a-cogs/36/N/YF/2023/6/S2B_36NYF_20230605_0_L2A/"
    nir_band_path = os.path.join(sentinel_path, "B08.tif")
    red_band_path = os.path.join(sentinel_path, "B04.tif")
    nir_data = rioxarray.open_rasterio(nir_band_path)
    red_data = rioxarray.open_rasterio(red_band_path)

    polygon_gdf = gpd.read_file(geojson_data)
    polygon_gdf = polygon_gdf.to_crs(nir_data.rio.crs)

    masked_nir = nir_data.rio.clip(polygon_gdf.geometry)
    masked_red = red_data.rio.clip(polygon_gdf.geometry)

    ndvi = (masked_nir - masked_red) / (masked_nir + masked_red)

    ndvi_array = ndvi.values

    output_png_path = f"ndvi_{polygon_id}.png"
    plt.imsave(output_png_path, ndvi_array, cmap='viridis')

    mean_ndvi = np.nanmean(ndvi_array)
    min_ndvi = np.nanmin(ndvi_array)
    max_ndvi = np.nanmax(ndvi_array)

    return Response({
        'mean_ndvi': mean_ndvi,
        'min_ndvi': min_ndvi,
        'max_ndvi': max_ndvi,
        'png_path': output_png_path,
    })
