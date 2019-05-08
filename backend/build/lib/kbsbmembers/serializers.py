# original Copyright Ruben Decrop
# modifications by Chessdevil Consulting BVBA

import base64
from rest_framework import serializers
from .models import *

class MemberBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription

        fields = [
            'id', 'first_name', 'last_name', 'category', 'ratingbel',
            'ratingfide', 'gender',
        ]

class MemberDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription

        fields = [
            'id', 'first_name', 'last_name', 'category', 'ratingbel',
            'ratingfide', 'gender',
        ]

