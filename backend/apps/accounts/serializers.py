from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para o perfil do usuário."""
    
    class Meta:
        model = UserProfile
        fields = [
            'monthly_income_goal', 'monthly_expense_limit', 'emergency_fund_goal',
            'email_notifications', 'anomaly_alerts', 'budget_alerts'
        ]


class UserSerializer(serializers.ModelSerializer):
    """Serializer para dados do usuário."""
    
    profile = UserProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'currency', 'timezone', 'profile', 'password', 'password_confirm',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'As senhas não coincidem.'
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer customizado para JWT tokens."""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Adicionar dados customizados ao token
        token['email'] = user.email
        token['full_name'] = user.full_name
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Adicionar dados do usuário na resposta
        data['user'] = UserSerializer(self.user).data
        
        return data


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de novos usuários."""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'As senhas não coincidem.'
            })
        
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({
                'email': 'Este email já está em uso.'
            })
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Criar perfil
        UserProfile.objects.create(user=user)
        
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para mudança de senha."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'As senhas não coincidem.'
            })
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Senha atual incorreta.')
        return value


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Serializer para atualização do perfil."""
    
    profile = UserProfileSerializer()
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'currency', 'timezone', 'profile'
        ]
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        # Atualizar dados do usuário
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Atualizar perfil
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance
