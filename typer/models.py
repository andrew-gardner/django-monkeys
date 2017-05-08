from django.db import models


# TODO: Add a Die database entry to group all dieImages
# class Die(models.Model)


class DieImage(models.Model):
    chipName = models.CharField('Chip Name', max_length=256)    # TODO: ForeignKey back to the chip database entry
    cropRow = models.IntegerField('Cropped Row')
    cropCol = models.IntegerField('Cropped Column')
    dieImage = models.ImageField('Die Image')

    def __str__(self):
        return ("%04d_%s_%d_%d" % (self.id, self.chipName, self.cropCol, self.cropRow))


class TypedDie(models.Model):
    dieImage = models.ForeignKey(DieImage, on_delete=models.CASCADE)
    typedField = models.TextField('Typed Info')

    def __str__(self):
        return ('TypedDie %d for dieImage %d' % (self.id, self.dieImage.id))
