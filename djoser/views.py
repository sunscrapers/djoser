from rest_framework import status, generics, filters
from rest_framework import viewsets
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from rest_framework.permissions import IsAuthenticated
from auth_system.models import *
from auth_system.serializers import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.http import require_http_methods
from asset.views import *
from django.db.models import Count
from rest_framework.pagination import PageNumberPagination
from templated_mail.mail import BaseEmailMessage
from django.contrib.auth.tokens import default_token_generator
from djoser import utils
from djoser.conf import settings as djoser_settings
import datetime


def home(request):
    return render(request, 'index.html', {})

def download(request):
    return render(request, 'download.html', {})

def profile(request):
    user = request.user
    return render(request, 'account/profile.html', {'user': user})


def login(request):
    return render(request, 'login.html', {})


def register(request):
    return render(request, 'register.html', {})


def activateAccount(request, uid, token):
    return render(request, 'activate.html', {'uid': uid, 'token': token})


def forgot_password(request):
    return render(request, 'forgot_password.html', {})


def reset_password(request, uid, token):
    return render(request, 'reset_password.html', {'uid': uid, 'token': token})


class ActivationEmail(BaseEmailMessage):
    template_name = 'email/mail-verify-email.html'
    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = djoser_settings.ACTIVATION_URL.format(**context)
        context["subject"] = MessageEmail.objects.filter(id=68).first().subject
        message = MessageEmail.objects.filter(id=68).first().template_message
        context["message"]=message.replace('[', '').replace(']', '').replace('TokenExpiration','3').replace('UserName',user.name).replace('InvitedFirstName',user.name).replace('Token',context["token"]).replace('Uid',context["uid"]).replace('BackendUrl',settings.BACK_END_URL).replace('FrontendUrl',settings.FRONT_END_URL)
        return context
    
class ConfirmationEmail(BaseEmailMessage):
    template_name = 'email/mail-verify-email.html'
    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        context["subject"] = MessageEmail.objects.filter(id=128).first().subject
        message = MessageEmail.objects.filter(id=128).first().template_message
        context["message"]=message.replace('[', '').replace(']', '').replace('UserName',user.name).replace('InvitedFirstName',user.name).replace('BackendUrl',settings.BACK_END_URL).replace('FrontendUrl',settings.FRONT_END_URL)
        return context



class PasswordChangedConfirmationEmail(BaseEmailMessage):
    template_name = 'email/mail-verify-email.html'
    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        subject = MessageEmail.objects.filter(id=127).first().subject
        context["subject"] = subject.replace('[', '').replace(']', '').replace('UserDetailName','password')
        message = MessageEmail.objects.filter(id=127).first().template_message
        context["message"]=message.replace('[', '').replace(']', '').replace('UserName',user.name).replace('UserDetailName','password').replace('New password: NewUserDetail','').replace('BackendUrl',settings.BACK_END_URL).replace('FrontendUrl',settings.FRONT_END_URL)
        return context

class UsernameChangedConfirmationEmail(BaseEmailMessage):
    template_name = 'email/mail-verify-email.html'
    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        subject = MessageEmail.objects.filter(id=127).first().subject
        context["subject"] = subject.replace('[', '').replace(']', '').replace('UserDetailName','username')
        message = MessageEmail.objects.filter(id=127).first().template_message
        context["message"]=message.replace('[', '').replace(']', '').replace('UserName',user.name).replace('UserDetailName','username').replace('NewUserDetail',user.name).replace('BackendUrl',settings.BACK_END_URL).replace('FrontendUrl',settings.FRONT_END_URL)
        return context

class EmailChangedConfirmationEmail(BaseEmailMessage):
    template_name = 'email/mail-verify-email.html'
    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        subject = MessageEmail.objects.filter(id=127).first().subject
        context["subject"] = subject.replace('[', '').replace(']', '').replace('UserDetailName','email')
        message = MessageEmail.objects.filter(id=127).first().template_message
        context["message"]=message.replace('[', '').replace(']', '').replace('UserName',user.name).replace('UserDetailName','email').replace('NewUserDetail',user.email).replace('BackendUrl',settings.BACK_END_URL).replace('FrontendUrl',settings.FRONT_END_URL)
        return context

    
@csrf_exempt
def change_user_account_activation(request):
    if request.method == 'POST':
        try:
            user = UserAccount.objects.get(email=request.POST.get('email'))
            is_activated = True if request.POST.get(
                'active') == 'true' else False
            if user:
                user.activated = is_activated
                user.save()
                key = 'Activated' if is_activated else 'Deactivated'
                json_response = {"success": True,
                                 "Message": 'User ' + key + ' Successfully'}
            else:
                json_response = {"error": "User Not Found", "success": False}
        except Exception as ex:
            json_response = {"error": str(ex), "success": False}
    else:
        json_response = {"error": 'Not Allowed Method', "success": False}
    return JsonResponse(json_response)


@api_view(['GET', 'POST'])
def List_following(request):
    pass

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10

class ResultsSetPagination(PageNumberPagination):
    page = DEFAULT_PAGE
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'total': self.page.paginator.count,
            # can not set default = self.page
            'page': int(self.request.GET.get('page', DEFAULT_PAGE)),
            'page_size': int(self.request.GET.get('page_size', self.page_size)),
            'results': data
        })

class allUsers(generics.ListAPIView):
    queryset = UserAccount.objects.all().order_by('id')
    search_fields = ['id', 'name', 'email', 'phone_number']
    ordering_fields = ['name', 'id']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    serializer_class = UserAccountSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        # this fnct return all user aren't in the dont recommanded List
        id_user = self.request.user.id
        blocked = BlackListChannels.objects.filter(
            user=id_user).values_list('channels', flat=True)
        queryset = UserAccount.objects.all().exclude(id__in=blocked).annotate(
            count=Count('follower')).order_by('-count')
        return queryset


class ALLFollowedUsers(generics.ListAPIView):
    queryset = Following.objects.all().order_by('id')
    ordering_fields = ['user__name', 'user__created_at']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    serializer_class = FollowerSerializer
    pagination_class = ResultsSetPagination


class FollowedUsers(generics.ListAPIView):
    queryset = Following.objects.all().order_by('id')
    search_fields = ['user__id', 'user__name', 'user__email']
    ordering_fields = ['user__name', 'user__created_at']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    serializer_class = FollowerSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        follower = self.kwargs.get("user")
        queryset = UserAccount.objects.all().filter(id=follower)
        return queryset


"""
  this Function return user how I follow
  -the id in is the id of user
  - follower is the list of user I follow

"""


class GetFollowed(generics.ListAPIView):

    queryset = Following.objects.all().order_by('id')
    search_fields = ['id', 'name', 'email', 'description']
    ordering_fields = ['name', 'id']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    serializer_class = UserAccountSerializer
    pagination_class = ResultsSetPagination
    # def get(self, request, id, *args, **kwargs):

    def get_queryset(self):
        queryset = Following.objects.filter(user=self.kwargs.get("id"))
        user_ids = []
        for obj in queryset:
            user_ids = queryset.values("follower")
        response = UserAccount.objects.filter(id__in=user_ids)
        return response

    """
  this Function return user how  following me
    -the id in is the id of user
  - the follower in output is the list following table of user following me
   """


class FollowingUsers(generics.ListAPIView):

    queryset = Following.objects.all().order_by('id')
    search_fields = ['id', 'name', 'email', 'description']
    ordering_fields = ['name', 'id']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    serializer_class = UserAccountSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        followers = Following.objects.filter(
            follower__id=self.kwargs.get("id"))
        user_ids = []
        for obj in followers:
            user_ids.append(obj.user.id)
        response = UserAccount.objects.filter(id__in=user_ids)
        return response


"""
  This function returns true if the id user you provided in the parameter is followed by the current 
  user's registry otherwise it will return False
"""


class IsFollow(APIView):
    serializer_class = FollowerSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        followers = data["follower"]
        if Following.objects.filter(user=request.user, follower__id=followers).exists():
            return Response(data={'message': True})
        else:
            return Response(data={'message': False})


class follow(generics.CreateAPIView):
    queryset = Following.objects.all().order_by('id')
    serializer_class = FollowerSerializer


class followCreate(generics.CreateAPIView):
    serializer_class = FollowerSerializer
    #http_method_names = ["patch"]

    def create(self, request, pk, format=None):
        ins_following = Following.objects.filter(
            user=self.kwargs.get("pk")).last()
        following = Following.objects.filter(
            follower=self.kwargs.get("pk")).last()
        data = request.data
        user = self.kwargs.get("pk")
        followers = data["follower"]
        print("before")
        print(followers)
        if not ins_following:
            user_found = UserAccount.objects.filter(id=user).last()
            print(user_found.id)
            ins_following = Following()
            ins_following.user = user_found
            # ins_following.follower.add(followers)
            ins_following.save()

        ins_following.follower.add(followers)
        ins_following.save()

        serializer = FollowerSerializer(ins_following)
        number_f = ins_following.follower.count()
        number_following = Following.objects.filter(follower=user).count()
        result = serializer.data
        result['count follower'] = number_f
        result['count following'] = number_following

        return Response(result)


class UpdateFollow(generics.UpdateAPIView):
    serializer_class = FollowerSerializer
    #http_method_names = ["patch"]

    def update(self, request, pk, format=None):
        ins_following = Following.objects.get(user=self.request.user)
        num_following = Following.objects.filter(
            follower=self.request.user).count()
        if (num_following >= 1):
            ins_following = Following.objects.get(user=self.request.user)
            data = request.data
            followers = data["follower"]
            # for f in followers :
            ins_following.follower.add(followers)
            ins_following.save()
            serializer = FollowerSerializer(ins_following)
            return Response(serializer.data)
        else:
            return redirect('create_follow', pk=self.kwargs.get("pk"))


class delfollow(generics.DestroyAPIView):

    """
    this endpoint delete all record of following user
    """

    serializer_class = FollowerSerializer

    def delete(self, request, pk, format=None):
        user = self.kwargs.get("pk")
        obj = Following.objects.filter(user=user)
        obj.delete()
        return Response(status=204)
        print('yser Folllowed model deleted')


class unfollow(generics.DestroyAPIView):
    """
    this endpoint delete specific follower of  user
    """
    serializer_class = FollowingSerializer

    def delete(self, request, pk, format=None):
        ins_following = Following.objects.get(user=self.kwargs.get("pk"))
        folloing = ins_following.follower.all()
        ins_following.follower.remove(pk)
        serializer = FollowerSerializer(ins_following)
        return Response(serializer.data)


class UserById(generics.ListAPIView):
    queryset = UserAccount.objects.all().order_by('id')
    serializer_class = UserAccountSerializer

    def get_queryset(self):
        by_id = self.kwargs.get("id")
        queryset = UserAccount.objects.all().filter(id=by_id)
        return queryset


"""
   returns user information
"""


class GetUserByEmail(generics.ListAPIView):
    serializer_class = UserAccountSerializer

    def get_queryset(self):
        email = self.kwargs.get("email")
        queryset = UserAccount.objects.filter(email=email)
        return queryset


class UpdateUser(generics.UpdateAPIView):
    queryset = UserAccount.objects.all().order_by('id')
    serializer_class = UserAccountSerializer
    http_method_names = ["patch"]


class Teams(generics.ListAPIView):
    queryset = Team.objects.all().order_by('id')
    serializer_class = TeamSerializer

    def get_queryset(self):
        organization = self.kwargs.get("organization")
        queryset = Team.objects.filter(organization_id=organization)
        return queryset


class getOrganization(generics.RetrieveAPIView):
    queryset = Organization.objects.all().order_by('id')
    serializer_class = OrganizationSerializer


class listOrganizations(generics.ListAPIView):
    queryset = Organization.objects.all().order_by('id')
    serializer_class = OrganizationSerializer


class allBlackChannels(generics.ListAPIView):
    queryset = BlackListChannels.objects.all().order_by('BlackList_id')
    search_fields = ['BlackList_id', 'channels', 'user']
    filter_backends = (filters.SearchFilter,)
    serializer_class = BlackListChannelsSerializer
    pagination_class = ResultsSetPagination


class BlackChannelsByUser(generics.ListAPIView):
    queryset = BlackListChannels.objects.all().order_by('BlackList_id')
    serializer_class = BlackListChannelsSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        id = self.kwargs.get("pk")
        queryset = BlackListChannels.objects.filter(user=id)
        return queryset


class BlackChannels(generics.ListAPIView):
    queryset = BlackListChannels.objects.all().order_by('BlackList_id')
    serializer_class = BlackListChannelsSerializer

    def get_queryset(self):
        BlackListChannels = self.kwargs.get("BlackList_id")
        queryset = BlackListChannels.objects.filter(BlackList_id=BlackListChannels)
        return queryset


class DeleteBlackChannels(generics.DestroyAPIView):
    queryset = BlackListChannels.objects.all().order_by('BlackList_id')
    serializer_class = BlackListChannelsSerializer


class CreateBlackChannels(generics.CreateAPIView):
    queryset = BlackListChannels.objects.all().order_by('BlackList_id')
    serializer_class = BlackListChannelsSerializer


class UpdateBlackChannels(generics.UpdateAPIView):
    queryset = BlackListChannels.objects.all().order_by('BlackList_id')
    serializer_class = BlackListChannelsSerializer
    http_method_names = ["patch"]


class ChangePasswordView(generics.UpdateAPIView):

    queryset = UserAccount.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer


class UpdateProfileView(generics.UpdateAPIView):

    queryset = UserAccount.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserSerializer


class MasterDataForUser(generics.ListAPIView):
    queryset = UserAccount.objects.all().order_by('id')
    serializer_class = MasterDataUserSerializer

    def get_queryset(self):
        mail = self.kwargs.get("email")
        queryset = [UserAccount.objects.filter(email=mail)][0]
        return queryset


class MasterDataAll(generics.ListAPIView):
    serializer_class = MasterDataUserSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        return UserAccount.objects.all()

class MasterDataAll(generics.ListAPIView):
    serializer_class = MasterDataUserSerializer
    search_fields = ['name', 'email']
    filter_backends = (filters.SearchFilter,)
    serializer_class = MasterDataUserSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        return UserAccount.objects.all()


class MasterDataAllForInvited(generics.ListAPIView):
    serializer_class = MasterDataUserSerializer
    search_fields = ['first_name','last_name', 'email_invited']
    filter_backends = (filters.SearchFilter,)
    serializer_class = MasterDataUserForInvitedSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        return InviteEmail.objects.all()


class MasterDataAllForInvitedByMe(generics.ListAPIView):
    serializer_class = MasterDataUserSerializer
    search_fields = ['first_name','last_name', 'email_invited']
    filter_backends = (filters.SearchFilter,)
    serializer_class = MasterDataUserForInvitedSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        me=UserAccount.objects.get(id=self.request.user.id)
        print('test  yes or no exicst')
        return InviteEmail.objects.filter(invited_by=me)


class MasterDataStatistic(APIView):
    serializer_class = MasterDataUserSerializer
    serializer_class = UserAccount

    def get(self, request,*args, **kwargs):
        list_of_static={key: " " for key in ['total_user', 'tester', 'player','content_creator','user_role']}
        list_of_static['total_user']=UserAccount.objects.all().count()
        list_of_static['tester']=UserAccount.objects.all().filter(access='Web+Mobile').count()
        list_of_static['player']=UserAccount.objects.all().filter(access='Mobile').count()
        list_of_static['content_creator']=UserAccount.objects.all().filter(access='Web+Mobile').count()
        return Response(list_of_static)

class ListStatus(APIView):
    
    def get(self, request,*args, **kwargs):
        list_of_static=[{id:1,name:'Approved'},{id:1,name:'Pending'},{id:1,name:'Rejected'}]
        return Response(list_of_static)

class UpdateWithlisted(generics.UpdateAPIView):
    serializer_class=UpdateWithlistedSerializer
    def update(self, request, pk, format=None):
        data=request.data
        status=data["approval_status"]
        approved_by=None
        approved_date=None
        if status == "Approved":
            approved_date=datetime.datetime.now() 
            user=UserAccount.objects.filter(id=pk).first()
            approved_by=request.user.id
        UserAccount.objects.filter(id=pk).update(approval_status=status,mobile_status=status,web_status=status, whitelisted_at = None, approved_at = approved_date,  approved_by =approved_by)
        profile= apps.get_model('user_profile', 'Profile').objects.filter(user_id=user.id).first()
        invite= UserAccount.objects.get(id=pk)
        InviteEmail.objects.filter(email_invited=invite).update(approved_by=approved_by, approved_date = approved_date, mobile_web_status = 'Approved',invite_status=7)
        msg_withlisted=MessageEmail.objects.filter(id=114).first()
        if msg_withlisted != None :
            custom_msg= msg_withlisted.template_message.replace('[', '').replace(']', '')
            custom_msg= custom_msg.replace('InvitedFirstNameLastName',profile.first_name +' '+profile.last_name )
            custom_msg=custom_msg.replace('InvitedLastName',profile.last_name )
            custom_msg=custom_msg.replace('InvitedFirstName',profile.first_name)
            custom_msg=custom_msg.replace('BackendUrl',settings.BACK_END_URL)
            custom_msg=custom_msg.replace('FrontendUrl',settings.FRONT_END_URL)
            msg_html = render_to_string('email/complish-email.html',{'message':custom_msg})
            send_mail("Ready, set, go! ", 
                            " ",
                            'noreply@abxrstudio.com',
                            [invite,],
                            fail_silently=False,
                            auth_user=None,
                            auth_password=None,
                            connection=None,
                            html_message=msg_html )
        return Response({"message": "Status updated successfully"})


class FilterMasterDataAll(generics.ListAPIView):
    queryset = UserAccount.objects.all().order_by('id')
    search_fields = ['email','name']
    filter_backends = (filters.SearchFilter,)
    serializer_class = MasterDataUserSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        
        role_category=self.request.GET.getlist('role_category')
        role_subcategory=self.request.GET.getlist('role_subcategory')
        status_mobile=self.request.GET.getlist('status_mobile')
        status_web=self.request.GET.getlist('status_web')
        acquisition_source_method=self.request.GET.getlist('acquisition_source_method')
        acquisition_source_type=self.request.GET.getlist('acquisition_source_type')
        acquisition_source_invited_by_name=self.request.GET.getlist('acquisition_source_invited_by_name')
        acquisition_whitelist_date_added=self.request.GET.getlist('acquisition_whitelist_date_added')
        acquisition_approval_status=self.request.GET.getlist('acquisition_approval_status')
        acquisition_approval_by=self.request.GET.getlist('acquisition_approval_by')
        acquisition_approval_date_approved=self.request.GET.getlist('acquisition_approval_date_approved')
        onboarding_status_first_date_sent=self.request.GET.getlist('onboarding_status_first_date_sent')
        onboarding_status_first_status=self.request.GET.getlist('onboarding_status_first_status')
        onboarding_status_confirmation_date_sent=self.request.GET.getlist('onboarding_status_confirmation_date_sent')
        onboarding_status_confirmation_signup_status=self.request.GET.getlist('onboarding_status_confirmation_signup_status')
        onboarding_status_completion_date_started=self.request.GET.getlist('onboarding_status_completion_date_started')
        onboarding_status_completion_date_completed=self.request.GET.getlist('onboarding_status_completion_date_completed')
        onboarding_status_reminder_completion=self.request.GET.getlist('onboarding_status_reminder_completion')
        onboarding_status_mobile_app_date=self.request.GET.getlist('onboarding_status_mobile_app_date')
        onboarding_status_mobile_app_status=self.request.GET.getlist('onboarding_status_mobile_app_status')
        profile_phone_number=self.request.GET.getlist('profile_phone_number')
        profile_country=self.request.GET.getlist('profile_country')
        profile_city=self.request.GET.getlist('profile_city')
        profile_birth=self.request.GET.getlist('profile_birth')
        profile_age=self.request.GET.getlist('profile_age')
        profile_gender=self.request.GET.getlist('profile_gender')
        profile_race=self.request.GET.getlist('profile_race')
        profile_is_hispanic =self.request.GET.getlist('profile_is_hispanic')
        profile_interest_area=self.request.GET.getlist('profile_interest_area')
        profile_phone_number=self.request.GET.getlist('onboarding_status_mobile_app_status')
        profile_timezone=self.request.GET.getlist('onboarding_status_mobile_app_status')
        profile_education_level=self.request.GET.getlist('profile_education_level')
        profile_credit_card=self.request.GET.getlist('profile_credit_card')
        profile_is_hispanic=self.request.GET.getlist('profile_is_hispanic')
        project_settings_title=self.request.GET.getlist('project_settings_title')
        project_settings_description=self.request.GET.getlist('project_settings_description')
        project_settings_team=self.request.GET.getlist('project_settings_team')
        project_settings_display_device=self.request.GET.getlist('project_settings_display_device')
        project_settings_device_maker=self.request.GET.getlist('project_settings_device_maker')
        project_settings_experience=self.request.GET.getlist('project_settings_experience')
        project_settings_surf_option=self.request.GET.getlist('project_settings_surf_option')
        project_settings_camera_option =self.request.GET.getlist('project_settings_camera_option')
        project_settings_final_product=self.request.GET.getlist('project_settings_final_product')
        project_settings_industry=self.request.GET.getlist('project_settings_industry')
        project_settings_public_private=self.request.GET.getlist('project_settings_public_private')
        project_settings_published=self.request.GET.getlist('project_settings_published')
        project_engagement_times_shared_with=self.request.GET.getlist('project_engagement_times_shared_with')
        project_engagement_list_of_shared_with=self.request.GET.getlist('project_engagement_list_of_shared_with')
        project_engagement_number_of_views=self.request.GET.getlist('project_engagement_number_of_views')
        project_engagement_number_of_liked=self.request.GET.getlist('project_engagement_number_of_liked')
        project_decision_tree_number_of_assets=self.request.GET.getlist('project_decision_tree_number_of_assets')
        project_decision_tree_number_of_scenes=self.request.GET.getlist('project_decision_tree_number_of_scenes')
        project_decision_tree_number_of_logic=self.request.GET.getlist('project_decision_tree_number_of_logic')
        project_decision_tree_characters=self.request.GET.getlist('project_decision_tree_characters')
        project_decision_tree_models=self.request.GET.getlist('project_decision_tree_models')
        project_decision_tree_effects=self.request.GET.getlist('project_decision_tree_effects')
        project_decision_tree_lights=self.request.GET.getlist('project_decision_tree_lights')
        project_decision_tree_sounds=self.request.GET.getlist('project_decision_tree_sounds')
        project_decision_tree_videos=self.request.GET.getlist('project_decision_tree_videos')
        project_decision_tree_images=self.request.GET.getlist('project_decision_tree_images')
        project_decision_tree_voice=self.request.GET.getlist('project_decision_tree_voice')
        project_decision_tree_animation=self.request.GET.getlist('project_decision_tree_animation')
        project_decision_tree_3d=self.request.GET.getlist('project_decision_tree_3d')
        project_decision_tree_timelength_of_simulation=self.request.GET.getlist('project_decision_tree_timelength_of_simulation')
        project_decision_tree_time_last_saved=self.request.GET.getlist('project_decision_tree_time_last_saved')
        project_decision_tree_time_last_published=self.request.GET.getlist('project_decision_tree_time_last_published')
        
        # from_date=self.request.query_params.get('from_date',None)
        if role_category:
            queryset =UserAccount.objects.filter(role__category__in=role_category)

        if role_subcategory:
            queryset=UserAccount.objects.filter(role__sub_category__in=role_subcategory)
        
        if status_mobile:
            queryset =UserAccount.objects.filter(web_status__in=status_mobile)

        if status_web:
            queryset=UserAccount.objects.filter(mobile_status__in=status_web)

        if acquisition_source_method:
            queryset=UserAccount.objects.filter(user_acquisition_method__in=acquisition_source_method)

        if acquisition_source_method:
            queryset=UserAccount.objects.filter(user_acquisition_method__in=acquisition_source_method)

        if acquisition_source_type:
            queryset=UserAccount.objects.filter(user_acquisition_type__in=acquisition_source_type)
        
        if acquisition_source_invited_by_name:
            queryset=UserAccount.objects.filter(invited_by__in=acquisition_source_invited_by_name)
        
        if acquisition_approval_status:
            queryset=UserAccount.objects.filter(approval_status__in=acquisition_approval_status)
        if acquisition_approval_by:
            queryset=UserAccount.objects.filter(approved_by__in=acquisition_approval_by)
        if acquisition_approval_date_approved:
            queryset=UserAccount.objects.filter(approved_at__in=acquisition_approval_date_approved)
        
        if onboarding_status_first_date_sent:
            invite_first=InviteEmail.objects.filter(invited_date__in=onboarding_status_first_date_sent).values('id')
            # list_invite_first=[]
            # for obj in invite_first:
            #     list_invite_first.append(obj.id)
            queryset=UserAccount.objects.filter(id__in=invite_first)
        
        if onboarding_status_first_status:
            invite_first=InviteEmail.objects.filter(mobile_web_status__in=onboarding_status_first_status).values('id')
            queryset=UserAccount.objects.filter(id__in=invite_first)
        
        if onboarding_status_confirmation_date_sent:
            invite_first=InviteEmail.objects.filter(date_of_confirm_email__in=onboarding_status_confirmation_date_sent).values('id')
            queryset=UserAccount.objects.filter(id__in=invite_first)
        
        if onboarding_status_confirmation_signup_status:
            status_of_invite=InviteStatu.objects.filter(category_name__in=onboarding_status_confirmation_signup_status).values('id')
            invite_first=InviteEmail.objects.filter(invite_status__in=status_of_invite).values('id')
            queryset=UserAccount.objects.filter(id__in=invite_first)
        
        if onboarding_status_completion_date_started:
            queryset=UserAccount.objects.filter(first_sing_up__in=onboarding_status_completion_date_started)
        
        if onboarding_status_completion_date_completed:
            queryset=UserAccount.objects.filter(last_sing_up__in=onboarding_status_completion_date_completed)
        
        if onboarding_status_reminder_completion:
            status_of_invite=InviteStatu.objects.filter(category_name__in=onboarding_status_reminder_completion).values('id')
            invite_first=InviteEmail.objects.filter(invite_status__in=status_of_invite).values('id')
            queryset=UserAccount.objects.filter(id__in=invite_first)
        
        if onboarding_status_mobile_app_date:
            invite_first=InviteEmail.objects.filter(invited_date__in=onboarding_status_mobile_app_date,access="Web+Mobile").values('id')
            queryset=UserAccount.objects.filter(id__in=invite_first)

        if onboarding_status_mobile_app_status:
            status_of_invite=InviteStatu.objects.filter(category_name__in=onboarding_status_mobile_app_status).values('id')
            invite_first=InviteEmail.objects.filter(invite_status__in=status_of_invite,access="Web+Mobile").values('id')
            queryset=UserAccount.objects.filter(id__in=invite_first)
        
        if profile_phone_number:
            queryset=UserAccount.objects.filter(phone_number__in=profile_phone_number)
        
        if profile_country:
            prof_user=Profile.objects.filter(country__in=profile_country).values('id')
            queryset=UserAccount.objects.filter(id__in=prof_user)

        if profile_city: 
            prof_user=Profile.objects.filter(city__in=profile_city).values('id')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        
        if profile_birth: 
            prof_user=Profile.objects.filter(date_of_birth__in=profile_birth).values('id')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        
        if profile_age:
            pass
        
        if profile_gender:
            # prof_user=Profile.objects.filter(date_of_birth__in=profile_birth).values('id')
            # queryset=UserAccount.objects.filter(gender__in=profile_gender)
            pass
        
        if profile_race:
            prof_user=Profile.objects.filter(race__in=profile_race).values('id')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        if profile_is_hispanic:
            prof_user=Profile.objects.filter(is_hispanic__in=profile_is_hispanic).values('id')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        if profile_interest_area:
            prof_user=Profile.objects.filter(interest_area__in=profile_interest_area).values('id')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        if profile_timezone:
            prof_user=Profile.objects.filter(timezone__in=profile_timezone).values('id')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        if profile_education_level:
            prof_user=Profile.objects.filter(education_level__in=profile_education_level).values('id')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        if profile_credit_card:
            pass
        
        if project_settings_title:
            prof_user=Project.objects.filter(title__in=project_settings_title).values('creator')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        if project_settings_description:
            prof_user=Project.objects.filter(subtitle__in=project_settings_description).values('creator')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        if project_settings_team:
            prof_user=Project.objects.filter(team_id__in=project_settings_team).values('creator')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        if project_settings_display_device:
            prof_user=Project.objects.filter(device__in=project_settings_display_device).values('creator')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        if project_settings_device_maker:
            prof_user=Project.objects.filter(device_maker__in=project_settings_device_maker).values('creator')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        if project_settings_experience:
            # prof_user=Project.objects.filter(education_level__in=project_settings_experience).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_settings_surf_option:
            prof_user=Project.objects.filter(surf_options__in=project_settings_surf_option).values('creator')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        if project_settings_camera_option :
            prof_user=Project.objects.filter(camera_type__in=project_settings_camera_option).values('creator')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        if project_settings_final_product:
            prof_user=Project.objects.filter(final_product__in=project_settings_final_product).values('creator')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        if project_settings_industry:
            prof_user=Project.objects.filter(industry__in=project_settings_industry).values('creator')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        if project_settings_public_private:
            prof_user=Project.objects.filter(privacy__in=project_settings_public_private).values('creator')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        if project_settings_published:
            # prof_user=Project.objects.filter(is_published__in=project_settings_published).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_engagement_times_shared_with:
            # prof_user=Project.objects.filter(education_level__in=project_engagement_times_shared_with).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_engagement_list_of_shared_with:
            prof_user=Project.objects.filter(shared_with__in=project_engagement_list_of_shared_with).values('creator')
            queryset=UserAccount.objects.filter(id__in=prof_user)
        if project_engagement_number_of_views:
            # prof_user=Project.objects.filter(education_level__in=project_engagement_number_of_views).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_engagement_number_of_liked:
            # prof_user=Project.objects.filter(education_level__in=profile_education_level).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass

        if project_decision_tree_number_of_assets:
            # prof_user=Project.objects.filter(education_level__in=project_decision_tree_number_of_assets).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_decision_tree_number_of_scenes:
            # prof_user=Project.objects.filter(education_level__in=profile_education_level).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_decision_tree_number_of_logic:
            # prof_user=Project.objects.filter(education_level__in=profile_education_level).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass

        if project_decision_tree_characters:
            # prof_user=Project.objects.filter(education_level__in=profile_education_level).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_decision_tree_models:
            # prof_user=Project.objects.filter(education_level__in=profile_education_level).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_decision_tree_effects:
            # prof_user=Project.objects.filter(education_level__in=profile_education_level).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_decision_tree_lights:
            # prof_user=Project.objects.filter(education_level__in=profile_education_level).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_decision_tree_sounds:
            # prof_user=Project.objects.filter(education_level__in=profile_education_level).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_decision_tree_videos:
            # prof_user=Project.objects.filter(education_level__in=profile_education_level).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_decision_tree_images:
            # prof_user=Profile.objects.filter(education_level__in=profile_education_level).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_decision_tree_voice:
            # prof_user=Profile.objects.filter(education_level__in=profile_education_level).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_decision_tree_animation:
            # prof_user=Profile.objects.filter(education_level__in=profile_education_level).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_decision_tree_3d:
            # prof_user=Profile.objects.filter(education_level__in=profile_education_level).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_decision_tree_timelength_of_simulation:
            # prof_user=Profile.objects.filter(education_level__in=profile_education_level).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_decision_tree_time_last_saved:
            # prof_user=Profile.objects.filter(education_level__in=profile_education_level).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        if project_decision_tree_time_last_published:
            # prof_user=Profile.objects.filter(education_level__in=profile_education_level).values('creator')
            # queryset=UserAccount.objects.filter(id__in=prof_user)
            pass
        return queryset



class GetEmailsVariablesId(generics.RetrieveAPIView):
    queryset = DynamicEmailVariables.objects.all().order_by('id')
    serializer_class = EmailsVariablesSerializer
    lookup_fields = ['id']


class UpdateEmailsVariables(generics.UpdateAPIView):
    queryset = DynamicEmailVariables.objects.all().order_by('id')
    serializer_class = EmailsVariablesSerializer
    http_method_names = ["patch"]


class DeleteEmailsVariables(generics.DestroyAPIView):
    queryset = DynamicEmailVariables.objects.all().order_by('id')
    serializer_class = EmailsVariablesSerializer


class ListEmailsVariables(generics.ListAPIView):
    queryset = DynamicEmailVariables.objects.all().order_by('id')
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)
    serializer_class = EmailsVariablesSerializer


class CreateEmailsVariables(generics.CreateAPIView):
    queryset = DynamicEmailVariables.objects.all().order_by('id')
    serializer_class = EmailsVariablesSerializer

