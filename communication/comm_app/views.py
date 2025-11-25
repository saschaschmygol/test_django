import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import MessageOut, Ticket, User, MessageIn  # Опционально
#from comm_project.settings import TELEGRAM_BOT_TOKEN
from .utils import send_telegram_message

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserSerializer


@api_view(['POST'])
def operator_reply(request):
    """ Принять сообщение от Operator и отправить пользователю"""
    # Ожидаемый payload: {'text': 'ответ оператора', 'ticket_id': id тикета}
    user_id = request.user.id
    text = request.data.get('text')
    ticket_id = request.data.get('ticket_id')

    user_id = User.objects.get(id=user_id)
    ticket_id = Ticket.objects.get(id=ticket_id)

    #для отправки в чат
    chat_id = request.data.get('chat_id')

    if not user_id or not text:
        return Response({'error': 'Missing user_id or text'}, status=status.HTTP_400_BAD_REQUEST)

    # Логируем
    MessageOut.objects.create(user=user_id, ticket_id=ticket_id, text=text)

    # Отправляем в Telegram
    send_telegram_message(chat_id, text)

    return Response({'status': 'sent'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def ticket_assign(request):
    ''' Назначение тикета '''
    user_id = request.user.id
    ticket_id = request.data.get("ticket_id")

    Ticket.objects.filter(id=ticket_id).update(user_id=user_id, status='appointed')
    return JsonResponse({'status': 'ok', 'ticket_id': ticket_id, 'user_id': user_id})

@api_view(['POST'])
def ticket_close(request):
    '''Закрытие тикета'''
    user_id = request.user.id
    ticket_id = request.data.get("ticket_id")

    Ticket.objects.filter(id=ticket_id).update(status='closed')
    return JsonResponse({'status': 'ok', 'ticket_id': ticket_id, 'user_id': user_id})


@api_view(['GET'])
def get_all_message_ticket(request):
    ''' Получение всех сообщений к тикету'''
    ticket_id = request.data.get("ticket_id")

    messages_in = list(MessageIn.objects.filter(ticket_id=ticket_id).values())
    messages_out = list(MessageOut.objects.filter(ticket_id=ticket_id).values())

    return JsonResponse({
        "ticket_id": ticket_id,
        "messages_in": messages_in,
        "messages_out": messages_out,
    })

@api_view(['GET'])
def get_ticket_user(request):
    '''Получение тикетов, привязанных к user'''
    user_id = request.user.id

    tickets = list(Ticket.objects.filter(user_id=user_id).values())
    return JsonResponse(tickets, safe=False)

@api_view(['GET'])
def get_all_ticket_open(request):
    '''Получение всех свободных тикетов'''

    tickets = list(Ticket.objects.filter(status="open").values())
    return JsonResponse(tickets, safe=False)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    from django.contrib.auth import authenticate
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)