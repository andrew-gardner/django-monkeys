from django.db import models


class SiteSettings(models.Model):
    """
    A collection of settings that can be defined site-wide.
    """
    introText = models.TextField('Intro Text', blank=True)

    def __str__(self):
        return ("Site settings:\nintroText:%s" % (self.introText))


class Die(models.Model):
    """
    A model storing information for a die that has been imaged.
    """
    name = models.CharField(max_length=256)
    instructions = models.TextField('Instructions', blank=True)

    def __str__(self):
        return ("%s" % (self.name))


class InstructionsImage(models.Model):
    """
    A class to hold an instruction image for the Die class' instructions.
    """
    die = models.ForeignKey(Die, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    image = models.ImageField('Die Image')

    def __str__(self):
        return ("Instructions image %s for Die %s" % (self.name, self.die.name))


class DieImage(models.Model):
    """
    One of the individual images associated with a referenced chip die.
    """
    die = models.ForeignKey(Die, on_delete=models.CASCADE)
    cropRow = models.IntegerField('Cropped Row')
    cropCol = models.IntegerField('Cropped Column')
    image = models.ImageField('Die Image')

    # These two are specific to images of ROMs
    # It's possible this should live in a subclass of DieImage someday
    bitWidth = models.IntegerField('Bits wide', default=0)
    bitHeight = models.IntegerField('Bits tall', default=0)

    def __str__(self):
        return ("%s_%02d_%02d" % (self.die.name, self.cropCol, self.cropRow))


class TypedDie(models.Model):
    """
    Contains typed text for a given die image.
    References back to the Die Image it's associated with.
    """
    dieImage = models.ForeignKey(DieImage, on_delete=models.CASCADE)
    submitter = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.DO_NOTHING)
    typedField = models.TextField('Typed Info', blank=True)
    submitDate = models.DateTimeField('Time Submitted', null=True, blank=True)

    def completed(self):
        """
        """
        return (self.typedField != "")

    def __str__(self):
        return ('TypedDie for DieImage "%s" (%r)' % (self.dieImage, self.completed()))

