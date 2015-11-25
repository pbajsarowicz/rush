from django.db import models


class Club(models.Model):
    name = models.CharField(max_length=128)
	

class Contest(models.Model):
    name = models.CharField(max_length=128)
    #date = models.DataTimeField()
