from django.db import models

class DieImage(models.Model):
    chipName = models.CharField('Chip Name', max_length=256)
    dieImageNum = models.IntegerField('Die Image Number')
    cropRow = models.IntegerField('Cropped Row')
    cropCol = models.IntegerField('Cropped Column')
    dieImage = models.ImageField('Die Image')

    def __str__(self):
        return ("%s_%d_%d_%d" % (self.chipName, self.dieImageNum, self.cropCol, self.cropRow))


class TypedDie(models.Model):
    dieImage = models.ForeignKey(DieImage, on_delete=models.CASCADE)
    typedField = models.TextField('Typed Info')

    def __str__(self):
        return ('TypedDie for dieImage %d' % dieImage.id)
