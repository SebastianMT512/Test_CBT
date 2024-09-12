from django.db import models

class Movie(models.Model):
   id = models.CharField(max_length=50,primary_key=True)
   title = models.CharField(max_length=50)
   country = models.CharField(max_length=30)
   rating = models.DecimalField(max_digits=3, decimal_places=1)
   
   def __str__(self):
       return self.title
    
   def clean(self):
      if(self.rating < 1.0 or self.rating > 5.0):
         raise ValidationError("Rating must be between 1 and 5")
      
