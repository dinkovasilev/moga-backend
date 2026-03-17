from django.urls import path
from django.contrib.auth.views import (
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from .views import (
        mobile_login,
        home,
        get_csrf_token,
        MyLoginView, 
        RegisterView,
        ChangeMail,
        profile,
        banlist,
        content,
        publications,
        inbox_list,
        MyTasksList,
        OwnTaskList,
        AllTasksList,
        ExternTaskList,
        WaitingTaskList,
        TaskInboxList,
        TaskMessageList,
        TaskHistory,
        MyTasksChatList,

        ItemInboxList,
        ItemMessageList,
        my_needs,
        my_itembox,
        
        OwnItemList,
        #MyItemsList,
        ExternItemList,
        AllItemsList,

        BanHero,
        unblock_user,
)


urlpatterns = [
    path('',home,name='home'),
    path('token/',get_csrf_token,name='get-token'),
    #path('mobile/login/', MobileLoginView.as_view(), name='mobile-login'),
    path('mobile/login/', mobile_login, name='mobile-login'),
    path('login/', MyLoginView.as_view(redirect_authenticated_user=True),name='login'),
    path('logout/', LogoutView.as_view(next_page='login'),name='logout'),
    path('register/', RegisterView.as_view(),name='register'),
    path('password-reset/', 
                PasswordResetView.as_view(
                template_name='player/password_reset.html',
                html_email_template_name='player/password_reset_email.html'
        ),
        name='password-reset'
    ),
    path('password-reset/done/', 
                PasswordResetDoneView.as_view(
                        template_name='player/password_reset_done.html'),
                        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
                PasswordResetConfirmView.as_view(
                        template_name='player/password_reset_confirm.html'),
                        name='password_reset_confirm'),
    path('password-reset-complete/',
                PasswordResetCompleteView.as_view(
                        template_name='player/password_reset_complete.html'),
                        name='password_reset_complete'),
    path('profile/', profile, name='profile'),
    path('change-mail/', ChangeMail.as_view(), name='change-mail'),
    path('banlist/',banlist,name='banlist'),    
    path('publications/',publications, name='publications'), 
    path('inbox/',inbox_list,name='inbox'),
    path('content/',content,name='content'),
    path('tasks/own/', OwnTaskList.as_view(),name='owntasks'),
    path('tasks/extern/', ExternTaskList.as_view(),name='externtasks'),
    path('tasks/waiting/', WaitingTaskList.as_view(),name='waitingtasks'),
    path('tasks/all/', AllTasksList.as_view(),name='alltasks'),
    path('tasks/mylist/', MyTasksList.as_view(),name='mytasks-list'),
    path('tasks/my-chat-list/', MyTasksChatList.as_view(),name='mytasks-chatlist'),
    path('tasks/inbox/',TaskInboxList.as_view(),name='tasks-inbox'),
    path('task/messages/<str:task_id>',TaskMessageList.as_view(),name='task-messages'),
    path('task/history/<str:task_id>',TaskHistory.as_view(),name='task-history'),

    path('items/myneeds/',my_needs, name='my-needs'),    
    path('items/mylist/',my_itembox,name='myitems-list'), #MyItemsList.as_view()
    path('items/own/',OwnItemList.as_view(),name='ownitems'),
    path('items/extern/',ExternItemList.as_view(),name='externitems'),
    path('items/all/', AllItemsList.as_view(),name='allitems'),
    path('items/inbox/',ItemInboxList.as_view(),name='items-inbox'),
    path('item/messages/<str:item_id>',ItemMessageList.as_view(),name='item-messages'),

    path('ban/<str:username>', 
            BanHero.as_view(),
            name='ban-hero'),
    path('unban/<str:username>', unblock_user, name='unban'),     
]