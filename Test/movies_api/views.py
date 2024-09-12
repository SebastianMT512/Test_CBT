from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Count, Case, When, IntegerField,  IntegerField, FloatField, ExpressionWrapper,F,Q
from .models import Movie
from .serializer import MovieSerializer

# Create your views here.
class MoviesApiView(viewsets.ModelViewSet):
   queryset = Movie.objects.all()
   serializer_class = MovieSerializer
   
   def get_Movie(self, id):
        try:
            return Movie.objects.get(id=id)
        except Movie.DoesNotExist:
            return None
   def get(self, request,id, *args, **kwargs):
      movies =  self.get_Movie(id=id)
      if not movies:
          return Response(
              {"res": "The element does not exist"}, status=status.HTTP_404_NOT_FOUND
          )
      serializer = MovieSerializer(movies, many=True)
      return Response(serializer.data, status = status.HTTP_200_OK)
   def post(self, request, *args, **kwargs):
        Movies = {
            "id": request.data.get("id"),
            "title": request.data.get("title"),
            "country": request.data.get("country"),
            "rating": request.data.get("rating")
        }
        serializer = MovieSerializer(data=Movies)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   def put(self, request, Movie_id, *args, **kwargs):
        Movies = self.get_Movie(Movie_id)
        if not Movies:
            return Response(
                {"res": "The element does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        Movies = {
            "id": request.data.get("id"),
            "title": request.data.get("title"),
            "country": request.data.get("country"),
            "rating": request.data.get("rating")
        }
        serializer = MovieSerializer(Movies, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   def delete(self, id, *args, **kwargs):
        movie = self.get_Movie(id)
        if not movie:
            return Response(
                {"res": "The element does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        movie.delete()
        return Response({"res": "The element was deleted"}, status=status.HTTP_200_OK)
     
   @action(methods=['get'], detail=False, name='top')
   def top(self, request):
       movies_top = Movie.objects.all().order_by('-rating')[:5]
       serializer = MovieSerializer(movies_top, many=True)
       return Response(serializer.data, status=status.HTTP_200_OK) 
     
   @action(methods=['get'], detail=False, name='summary')
   def summary(self, request):
       movies_country = Movie.objects.values('country').annotate(count=Count('country')).order_by('-count')
       serializer = MovieSerializer(movies_country, many=True)
       movies_by_rating = Movie.objects.annotate(
            rounded_rating=ExpressionWrapper(
                F('rating') * 10 / 1 / 10, 
                output_field=FloatField()
            )
        ).values('rounded_rating').annotate(total=Count('id')).order_by('rounded_rating')
       rating_ranges = Movie.objects.aggregate(
        rating_1=Count(Case(When(rating__gte=1.0, rating__lt=1.9, then=1), output_field=IntegerField())),
        rating_2=Count(Case(When(rating__gte=2.0, rating__lt=2.9, then=1), output_field=IntegerField())),
        rating_3=Count(Case(When(rating__gte=3.0, rating__lt=3.9, then=1), output_field=IntegerField())),
        rating_4=Count(Case(When(rating__gte=4.0, rating__lt=4.9, then=1), output_field=IntegerField())),
        rating_5=Count(Case(When(rating__gte=5.0, then=1), output_field=IntegerField()))
        )
       return Response({'movies_by_country': list(movies_country),
            'rating_ranges': rating_ranges}, status=status.HTTP_200_OK)
       
   @action(detail=False, methods=['get'], url_path='search')
   def search(self, request):
        query = request.query_params.get('q', None)
        sort_column = request.query_params.get('s', None)  
        sort_order = request.query_params.get('o', 'asc')
        if query:
            movies = Movie.objects.filter(Q(title__icontains=query) | Q(country__icontains=query))
            if sort_column:
                if sort_order == 'desc':
                    sort_column = f'-{sort_column}'  
                try:
                    movies = movies.order_by(sort_column)
                except Exception as e:
                    return Response({"error": f"Invalid sort column: {sort_column}"}, status=status.HTTP_400_BAD_REQUEST)
            serializer = MovieSerializer(movies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Search query not provided."}, status=status.HTTP_400_BAD_REQUEST)
        