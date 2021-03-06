from datetime import date
from itertools import product
from django.forms import ValidationError
from django.shortcuts import render,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from userinfo.models import *
from .serializers import *
from django.db.models import Q
from rest_framework import viewsets,generics,exceptions,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication ,TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from django.utils import timezone
import random

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


class Daily_MealSet(viewsets.ReadOnlyModelViewSet):
    queryset=Daily_Meal.objects.all()
    serializer_class = Daily_Mealserializers

class Meal_ProductSet(viewsets.ReadOnlyModelViewSet):
    queryset=MEAL_PRODUCT.objects.all()
    serializer_class = MEAL_PRODUCTserializers

class User_DetailSet(viewsets.ModelViewSet):
    queryset=User_Detail.objects.all()
    serializer_class=User_Detailserializers
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if(not self.queryset.filter(user=self.request.user).exists()):
            raise exceptions.ParseError("userdetail을 먼저 post해주세요")
        return self.queryset.filter(user=self.request.user)
    def perform_create(self, serializer):
        print(self.request.data)
        if(self.queryset.filter(user=self.request.user).exists()):
            raise exceptions.ParseError("이미 존재하는 userdetail")
        serializer.save(user=self.request.user)
    @action(detail=False,methods=['post'])
    def modify_user(self,request):      
        nowuser=self.request.user
        moduser=self.request.data
        qs=get_object_or_404(self.queryset,user=nowuser)
        qs.exercise = moduser.get('exercise',qs.exercise)
        if(qs.exercise!="low" and qs.exercise!="middle" and qs.exercise!="high"):
            raise exceptions.ParseError("exercise should be low middle high")
        qs.gender=moduser.get('gender',qs.gender)
        qs.height=moduser.get   ('height',qs.height)
        qs.weight=moduser.get('weight',qs.weight)
        qs.vegan_option=moduser.get('vegan_option',qs.vegan_option)
        qs.allergy=moduser.get('allergy',qs.allergy)
        qs.favor_category=moduser.get('favor_category',qs.favor_category)
        qs.avoid_category=moduser.get('avoid_category',qs.avoid_category)
        qs.save()
        serializer=self.get_serializer(qs)
        return Response(serializer.data)

class ProductSet(viewsets.ModelViewSet):
    queryset=Product.objects.all()
    serializer_class = Productserializers
    @action(detail=False)
    def plist(self,request):
        qs=self.queryset
        qparam_popular=request.query_params.get("popular")
        if(qparam_popular is not None):
            qs #이부분
        qparam_price_low_range=request.query_params.get("price_low")
        if(qparam_price_low_range is not None):
            if(not qparam_price_low_range.isdigit()):
                raise exceptions.ParseError("가격범위는 숫자만")
            qparam_price_low_range=int(qparam_price_low_range)
            qs=qs.filter(price__gte=qparam_price_low_range)
        qparam_price_high_range=request.query_params.get("price_high")
        if(qparam_price_high_range is not None):
            if(not qparam_price_high_range.isdigit()):
                raise exceptions.ParseError("가격범위는 숫자만")
            qparam_price_high_range=int(qparam_price_high_range)
            qs=qs.filter(price__lte=qparam_price_high_range)
        qparam_price_order=request.query_params.get("price_order")
        if(qparam_price_order is not None):
            if(qparam_price_order!="asc" and qparam_price_order!="desc"):
                raise exceptions.ParseError("product_price_order should be asc or desc")
            if(qparam_price_order=="asc"):
                qs=qs.order_by('price')
            if(qparam_price_order == "desc"):
                qs=qs.order_by('-price')
        qparam_product_name_order=request.query_params.get("product_name_order")
        if(qparam_product_name_order is not None):
            if(qparam_product_name_order!="asc" and qparam_product_name_order!="desc"):
                raise exceptions.ParseError("product_name_order should be asc or desc")
            if(qparam_product_name_order == "asc"):
                qs=qs.order_by('product_name')
            if(qparam_product_name_order == "desc"):
                qs=qs.order_by('-product_name')
        qparam_calory_order=request.query_params.get("calory_order")
        if(qparam_calory_order is not None):
            if(qparam_calory_order!="asc" and qparam_calory_order!="desc"):
                raise exceptions.ParseError("calory_order should be asc or desc")
            if(qparam_calory_order == "asc"):
                qs=qs.order_by('calory')
            if(qparam_calory_order == "desc"):
                qs=qs.order_by('-calory')
        qparam_product_name=request.query_params.get("product_name")
        if(qparam_product_name is not None):
            qs=qs.filter(product_name__icontains=qparam_product_name)
        qparam_calory_low_range=request.query_params.get("calory_low")
        if(qparam_calory_low_range is not None):
            if(not qparam_calory_low_range.isdigit()):
                raise exceptions.ParseError("칼로리는 숫자만")
            qparam_calory_low_range=int(qparam_calory_low_range)
            qs=qs.filter(calory__gte=qparam_calory_low_range)
        qparam_calory_high_range=request.query_params.get("calory_high")
        if(qparam_calory_high_range is not None):
            if(not qparam_calory_high_range.isdigit()):
                raise exceptions.ParseError("칼로리는 숫자만")
            qparam_calory_high_range=int(qparam_calory_high_range)
            qs=qs.filter(calory__lte=qparam_calory_high_range)
        serializer = self.get_serializer(qs,many=True)
        return Response(serializer.data)

    @action(detail=False)
    def order_by_name(self,request):
        qs=self.queryset.order_by('product_name')
        serializer= self.get_serializer(qs,many=True)
        return Response(serializer.data)  
    
    @action(detail=False)
    def order_by_rname(self,request):
        qs=self.queryset.order_by('-product_name')
        serializer= self.get_serializer(qs,many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def order_by_price(self,request):
        qs=self.queryset.order_by('price')
        serializer= self.get_serializer(qs,many=True)
        return Response(serializer.data)

    @action(detail=False)
    def order_by_rprice(self,request):
        qs=self.queryset.order_by('-price')
        serializer= self.get_serializer(qs,many=True)
        return Response(serializer.data)

class cut_by_price(viewsets.ReadOnlyModelViewSet):
    queryset=Product.objects.all().order_by('?')
    serializer_class=Productserializers
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if(not User_Detail.objects.filter(user=self.request.user).exists()):
            raise exceptions.ParseError("유저정보를 기입해주세요")
        price=self.request.query_params.get('price',None)
        low_salt=self.request.query_params.get('low_salt',None)
        low_calory=self.request.query_params.get('low_sugar',None)
        low_fat=self.request.query_params.get('low_fat',None)
        low_carbo=self.request.query_params.get('low_carbo',None)
        high_protein=self.request.query_params.get('high_protein',None) 
        rqs=self.queryset.order_by('?')
        if(low_salt!=None):
            rqs=rqs.filter(sodium__lte=480)
        if(low_fat!=None):
            rqs=rqs.filter(fat__lte=9)
        if(low_calory!=None):
            rqs=rqs.filter(calory__lte=500)
        if(high_protein!=None):
            rqs=rqs.filter(protein__gte=12)
        if(low_carbo!=None):
            rqs=rqs.filter(carbohydrate__lte=35)
        if(price==None):
            raise exceptions.ParseError("파라미터가 필요합니다 (가격)")
        if not price.isdigit():
            raise exceptions.ParseError("가격은 숫자만")
        price=int(price)
        if(price<1000):
            raise exceptions.ParseError("가격은 1000원이상")
        c=0
        cutcqs=[]
        for x in rqs:
            nowc=x.price
            if(nowc+c>price):
                break
            c+=nowc
            cutcqs.append(x)
        return cutcqs

class get_meal_list(viewsets.ReadOnlyModelViewSet):
    queryset=Daily_Meal.objects.all()
    serializer_class=Daily_Mealserializers
    permission_classes = [IsAuthenticated]
    def list(self, request, *args, **kwargs):
        meal_list= Daily_Meal.objects.filter(Q(user=self.request.user)&Q(created_at__date__gte=timezone.now().date()-timezone.timedelta(days=7)))
        mplist= MEAL_PRODUCT.objects.filter(meal_id__in=meal_list)
        serial=self.get_serializer(mplist,many=True)
        return Response(serial.data)

class meal_by_client(viewsets.ModelViewSet):
    queryset=Product.objects.all()
    serializer_class=Productserializers
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        product_list=request.data
        print(product_list)
        rqs=[]
        for x in product_list:
            meal_list= Daily_Meal.objects.filter(created_at__date=timezone.now().date())
            if(not self.queryset.filter(id=x['id']).exists()):
                raise exceptions.ParseError("존재하지않는 품목입니다")
            if(x['wtime']!="아침" and x['wtime']!="점심" and x['wtime']!="저녁"):
                raise exceptions.ParseError("아침 점심 저녁을 선택해주세요")
            meal_id=1
            if(x['wtime']=="아침"):
                if(not meal_list.filter(user=request.user,morning=True).exists()):
                    meal_id=Daily_Meal.objects.create(user=self.request.user,morning=True)
                else:
                    meal_id=meal_list.filter(morning=True)[0]
            if(x['wtime']=="점심"):
                if(not meal_list.filter(user=request.user,lunch=True).exists()):
                    meal_id=Daily_Meal.objects.create(user=self.request.user,lunch=True)
                else:
                    meal_id=meal_list.filter(lunch=True)[0]
            if(x['wtime']=="저녁"):
                if(not meal_list.filter(user=request.user,dinner=True).exists()):
                    meal_id=Daily_Meal.objects.create(user=self.request.user,dinner=True)
                else:
                    meal_id=meal_list.filter(dinner=True)[0]
            nowp=self.queryset.get(id=x['id'])
            MEAL_PRODUCT.objects.create(meal_id=meal_id,product_id=nowp)
            rqs.append(nowp)
        serial=self.get_serializer(rqs,many=True)
        return Response(serial.data)

# Create your views here.
