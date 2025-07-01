from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import UserProfile
from .serializers import (
    UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer,
    ChangePasswordSerializer, UpdateProfileSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """View para registro de novos usuários."""
    
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Gerar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """View customizada para obtenção de tokens JWT."""
    
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """View para logout (blacklist do refresh token)."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout realizado com sucesso."}, 
                          status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Token inválido."}, 
                          status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """View para visualizar e atualizar perfil do usuário."""
    
    serializer_class = UpdateProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """View para mudança de senha."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                "message": "Senha alterada com sucesso."
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """Retorna estatísticas do usuário."""
    user = request.user
    
    # Importar models aqui para evitar import circular
    from apps.transactions.models import Transaction, Category, Account
    
    stats = {
        'user_since': user.created_at,
        'total_transactions': Transaction.objects.filter(user=user).count(),
        'total_categories': Category.objects.filter(user=user, is_active=True).count(),
        'total_accounts': Account.objects.filter(user=user, is_active=True).count(),
        'this_month_transactions': Transaction.objects.filter(
            user=user,
            date__year=2024,
            date__month=12
        ).count()
    }
    
    return Response(stats)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_account(request):
    """Deleta a conta do usuário."""
    user = request.user
    
    # Confirmar com senha
    password = request.data.get('password')
    if not password or not user.check_password(password):
        return Response({
            'error': 'Senha incorreta.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Soft delete - desativar conta
    user.is_active = False
    user.save()
    
    return Response({
        'message': 'Conta desativada com sucesso.'
    }, status=status.HTTP_200_OK)
