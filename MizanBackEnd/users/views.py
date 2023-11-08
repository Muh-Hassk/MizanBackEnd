from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, NotFound
from .serializers import UserSerializer, MessageSerializer, ConversationSerializer, NotCaseSerializer
from .models import User, Conversations, notCase
import jwt, datetime
from .NLP_model import JusticeClassifier





# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = User.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('incorrect Password')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')


        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'id': user.id,
            'username': user.username,
            'jwt': token
        }
        return response

    class UserView(APIView):
        def get(self, request):
            pass


class UserView(APIView):

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('UnAuthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthenticated')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response


class CheckUsernameView(APIView):
    def get(self, request, username):
        # Check if the username is already taken in your database
        username_exists = User.objects.filter(username=username).exists()

        if username_exists:
            data = {'available': False}
        else:
            data = {'available': True}

        return Response(data)

class CheckEmailView(APIView):
    def get(self, request, email):
        # Check if the email is already registered in your database
        email_exists = User.objects.filter(email=email).exists()

        if email_exists:
            data = {'available': False}
        else:
            data = {'available': True}

        return Response(data)
class GetConversationView(APIView):

    def get(self, request, conversation_id):
        # get The Authinticated User JWT
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('UnAuthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthenticated')


        # Ensure the conversation belongs to the authenticated user
        conversation = Conversations.objects.filter(user = User.objects.filter(id=payload['id']).first(), id=conversation_id).first()

        if not conversation:
            return Response({'error': 'Conversation not found or does not belong to the user.'}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve related messages for the specific conversation
        messages = conversation.messages_set.all()

        # Serialize the conversation with its related messages
        serialized_conversation = ConversationSerializer(conversation).data
        serialized_messages = MessageSerializer(messages, many=True).data
        serialized_conversation['messages'] = serialized_messages

        return Response(serialized_conversation, status=status.HTTP_200_OK)

class GetConversationsView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('UnAuthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthenticated')



        # Retrieve conversations for the current user
        conversations = Conversations.objects.filter(
            user = User.objects.filter(id=payload['id']).first()).prefetch_related('messages_set')

        # Serialize the conversations with their related messages
        conversation_data = []
        for conversation in conversations:
            serialized_conversation = ConversationSerializer(conversation).data
            messages = conversation.messages_set.all()  # Get related messages
            serialized_messages = MessageSerializer(messages, many=True).data
            serialized_conversation['messages'] = serialized_messages
            conversation_data.append(serialized_conversation)

        return Response(conversation_data, status=status.HTTP_200_OK)

class DeleteConversationView(APIView):

    def delete(self, request, conversation_id):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('UnAuthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthenticated')

        try:
            # Ensure the conversation exists and belongs to the authenticated user
            conversation = Conversations.objects.get(id=conversation_id,user = User.objects.filter(id=payload['id']).first() )
        except Conversations.DoesNotExist:
            raise NotFound(detail="Conversation not found or does not belong to the user")

        conversation.delete()
        return Response(data={"detail": "Conversation Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)

class SendMessageView(APIView):

    def post(self, request, conversation_id):
        # Check if the user is authenticated
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('UnAuthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthenticated')

        user = User.objects.filter(id=payload['id']).first()
        message_content = request.data.get('content')

        if conversation_id == "new":
            # Create a new conversation and get its ID
            new_conversation_data = {'user': User.objects.filter(id=payload['id']).first().id, 'name': message_content[:15]}
            new_conversation_serializer = ConversationSerializer(data=new_conversation_data)

            if new_conversation_serializer.is_valid():
                new_conversation = new_conversation_serializer.save()
                conversation_id = new_conversation.id
            else:
                return Response(new_conversation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check if the conversation exists
        try:
            conversation = Conversations.objects.get(id=conversation_id, user = User.objects.filter(id=payload['id']).first())
        except Conversations.DoesNotExist:
            return Response({"error": "Conversation not found or does not belong to the user."}, status=status.HTTP_404_NOT_FOUND)

        # Continue with the message creation
        message_data = {'role': 'user', 'content': message_content, 'Conversations': conversation_id}
        message_data['user'] = User.objects.filter(id=payload['id']).first()
        message_serializer = MessageSerializer(data=message_data)

        if message_serializer.is_valid():
            message_serializer.save()
            return Response(conversation_id, status=status.HTTP_201_CREATED)
        else:
            return Response(message_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetAIresponseView(APIView):

    def save_not_case_data(self, user, conversation_id, message_content):
        not_case_data = {
            'user': user,
            'Conversations': conversation_id,
            'type': 'Unrecognized Pattern',
            'message': message_content
        }
        not_case_instance = notCase(**not_case_data)
        not_case_instance.save()

    def post(self, request, conversation_id):
        # Check if the user is authenticated
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        user = User.objects.filter(id=payload['id']).first()
        # Input for prediction
        message_content = request.data.get('content')

        # Load the model and make predictions
        model = JusticeClassifier('/Users/muhammedhassan/Desktop/Mizan/MizanBackEnd/MizanBackEnd/users/npl_classifier.h5',
                                  '/Users/muhammedhassan/Desktop/Mizan/MizanBackEnd/MizanBackEnd/users/tokenizer.pkl')
        prediction = model.predict([message_content], 0.993)

        # Process the prediction result
        if prediction == 1:
            message_contentAIResponse = ' Based on My Training I see that the First Party is the Winner'
        elif prediction == 0:
            message_contentAIResponse = 'Based on My Training I see that the Second Party is the Winner'
        else:
            message_contentAIResponse = 'That\'s not a Legal case please send me a Legal Case'
            self.save_not_case_data(user,conversation_id,message_content)


        # Save the message data
        message_data = {
            'role': 'system',
            'content': message_contentAIResponse,
            'Conversations': conversation_id
        }
        message_data['user'] = User.objects.filter(id=payload['id']).first()
        message_serializer = MessageSerializer(data=message_data)
        if message_serializer.is_valid():
            message_serializer.save()
            return Response(message_contentAIResponse, status=status.HTTP_200_OK)
        else:
            return Response(message_serializer.errors, status=status.HTTP_400_BAD_REQUEST)