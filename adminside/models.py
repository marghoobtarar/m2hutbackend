from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db.models.deletion import CASCADE
from UserAuth.models import User
import datetime
from django.utils import timezone
import jsonfield

# from django import forms



class WorkLogsBreakModel(models.Model):
    name = models.CharField(max_length = 300,
                            null=True,
                            help_text = 'this is types of break defined by the admin'
                            )
    created_at = models.DateTimeField(default=timezone.now,
                                        blank=True)
    
    updated_at = models.DateTimeField(default=timezone.now,
                                        blank=True)                                                           
    admin_id = models.ForeignKey(User, 
                                null=True,
                                on_delete=models.CASCADE, 
                                related_name='User.id+',
                                help_text='model for the work logs'
                                )

class WorkLogsModel(models.Model):
    user_id = models.ForeignKey(User, 
                                null=True,
                                on_delete=models.CASCADE, 
                                related_name='User.id+',
                                help_text='model for the work logs'
                                )
    created_at = models.DateTimeField(default=timezone.now,
                                        blank=True)
    end_at = models.DateTimeField(null=True ,blank=True)
    
    total_works_hours = models.TimeField(null=True,
                                        max_length=300,
                                        blank=True)
    total_break_time = models.CharField(
                                        max_length=300,
                                        null=True,
                                        blank=True)
    

class WorkLogsDetailsModel(models.Model):

    worklog_id = models.ForeignKey(WorkLogsModel,
                                null=True,
                                on_delete=models.CASCADE, 
                                related_name='WorkLogsModel.id+',
                                help_text='model for the work logs details'
                                )

    captured_image = models.FileField(upload_to = 'work_log_images',  null=True)
    address = models.CharField(max_length = 300,
                                null = True,
                                help_text = 'this is current address of work log'
                                )
    longitude = models.FloatField(null=True,
                                help_text = 'this is current latitude of work log'
                                )
    latitude = models.FloatField(null=True,
                                help_text = 'this is current longitute of work log'
                                )


    work_log_break_id =  models.ForeignKey(WorkLogsBreakModel, 
                                            null=True,
                                            on_delete = models.CASCADE, 
                                            related_name = 'WorkLogsBreakModel.id+',
                                            help_text = 'model for the work logs break'
                                            )  
    worklog = (
            ( 1 ,'CLOCK_IN'),
            ( 2 ,'CLOCK_OUT'),
            ( 3 ,'BREAK_IN'),
            ( 4 ,'BREAK_OUT')

          
        )
    worklog_type= models.CharField( max_length=20,  
                                    choices=worklog, 
                 
                                    blank=True, 
                                    default=1,
                
                                    help_text='clock in type' )
    created_at = models.DateTimeField(default=timezone.now,
                                        blank=True)
 
class NoticesModel(models.Model):
    admin_id = models.ForeignKey(User,
                                null=True,
                                on_delete=models.CASCADE, 
                                related_name='User.id+',
                                help_text= 'admin notices'
                                )
    # date = models.DateTimeField(default=timezone.now,
    #                                     blank=True)
    author = models.CharField(
                                        max_length=300,
                                        null=True,
                                        blank=True)
    image = models.ImageField(upload_to = 'noticesimage',  null=True)
    draft = models.BooleanField(default=False, null= True) 
    publish = models.BooleanField(default=False, null= True) 
    heading = models.CharField(
                                        max_length=300,
                                        null=True,
                                        blank=True)
    description = models.CharField(
                                        max_length=2000,
                                        null=True,
                                        blank=True)
    date = models.CharField(
                                        max_length=2000,
                                        null=True,
                                        blank=True)
    created_at = models.DateTimeField(default=timezone.now,
                                        blank=True)
    updated_at = models.DateTimeField(default=timezone.now,
                                        blank=True)



class StyleModel(models.Model):

    admin_id = models.ForeignKey(User, 
                                null=True,
                                on_delete=models.CASCADE, 
                                related_name='User.id+',
                                help_text='model for styling model'
                                )
    systemName = models.CharField(max_length=300,
                                    blank=True)

    systemEmail = models.EmailField(null=True ,
                                    blank=True)
    
    mainColor = models.CharField(null=True,
                                    max_length=300,
                                    blank=True)
    secondaryColor = models.CharField(max_length=300,
                                    null=True,
                                    blank=True)
    mainTextColor = models.CharField(max_length=300,
                                    null=True,
                                    blank=True)
    systemLogo = models.FileField(upload_to = 'style_images', 
                                    null=True)
    systemIcon = models.FileField(upload_to = 'style_images', 
                                    null=True)
    created_at = models.DateTimeField(default=timezone.now,
                                        blank=True)
    updated_at = models.DateTimeField(null=True,blank=True)


class TypographyModel(models.Model):

    admin_id = models.ForeignKey(User, 
                                null=True,
                                on_delete=models.CASCADE, 
                                related_name='User.id+',
                                help_text='model for typography'
                                )
    h1 = jsonfield.JSONField(blank=True)

    h2 = jsonfield.JSONField(blank=True)
    
    h3 = jsonfield.JSONField(blank=True)
    h4 = jsonfield.JSONField(blank=True)
    bodyText = jsonfield.JSONField(blank=True)
    created_at = models.DateTimeField(default=timezone.now,
                                        blank=True)
    updated_at = models.DateTimeField(null=True,blank=True)



class RegisterEmailModel(models.Model):

    admin_id = models.ForeignKey(User, 
                                null=True,
                                on_delete=models.CASCADE, 
                                related_name='User.id+',
                                help_text='model for register email'
                                )
    heading = models.CharField(max_length=300,
                                null=True    )
    description = models.CharField(max_length=2000,
                                null=True    )
    created_at = models.DateTimeField(default=timezone.now,
                                        blank=True)
    updated_at = models.DateTimeField(null=True,blank=True)

class SuspensionEmailModel(models.Model):

    admin_id = models.ForeignKey(User, 
                                null=True,
                                on_delete=models.CASCADE, 
                                related_name='User.id+',
                                help_text='model for suspension email'
                                )
    heading = models.CharField(max_length=300,
                                null=True    )
    description = models.CharField(max_length=2000,
                                null=True    )
    created_at = models.DateTimeField(default=timezone.now,
                                        blank=True)
    updated_at = models.DateTimeField(null=True,blank=True)


class AdminEmailModel(models.Model):

    admin_id = models.ForeignKey(User, 
                                null=True,
                                on_delete=models.CASCADE, 
                                related_name='User.id+',
                                help_text='model for the work logs'
                                )
    smtpHostName = models.CharField(max_length=300,
                                null=True    )
    smtpPort = models.CharField(max_length=2000,
                                null=True    )
    smtpUser = models.CharField(max_length=300,
                                null=True    )
    smtpPassword = models.CharField(max_length=2000,
                                null=True    )
                                
    smtpAddress = models.CharField(max_length=2000,
                                null=True    )
    fromName = models.CharField(max_length=2000,
                                null=True    )
    created_at = models.DateTimeField(default=timezone.now,
                                        blank=True)
    updated_at = models.DateTimeField(null=True,
                                        blank=True)

