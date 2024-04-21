"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from business.api.auth import login, signup, testLogin, logout, manager_login, manager_logout
from business.api.paper_details import like_paper, score_paper, collect_paper, report_comment, comment_paper, \
    batch_download_papers, get_paper_info, get_first_comment, get_second_comment, like_comment
from business.api.update_document import upload_paper, remove_uploaded_paper, document_list
from business.api import user_info, manage
from business.api.search import vector_query, dialog_query, flush

urlpatterns = [
                  path("admin/", admin.site.urls),

                  # 用户及管理员认证模块
                  path("api/login", login),
                  path("api/sign", signup),
                  path("api/testLogin", testLogin),
                  path("api/logout", logout),
                  path("api/managerLogin", manager_login),
                  path("api/managerLogout", manager_logout),

                  # 论文详情界面
                  path("api/userLikePaper", like_paper),
                  path("api/userScoring", score_paper),
                  path("api/collectPaper", collect_paper),
                  path("api/reportComment", report_comment),
                  path("api/commentPaper", comment_paper),
                  path("api/batchDownload", batch_download_papers),
                  path("api/getPaperInfo", get_paper_info),
                  path("api/getComment1", get_first_comment),
                  path("api/getComment2", get_second_comment),
                  path("api/likeComment", like_comment),

                  # 用户上传论文模块
                  path("api/uploadPaper", upload_paper),
                  path("api/removeUploadedPaper", remove_uploaded_paper),
                  path("api/userInfo/documents", document_list),

                  # 个人信息模块
                  path("api/userInfo/userInfo", user_info.user_info),
                  path("api/userInfo/avatar", user_info.modify_avatar),
                  path("api/userInfo/collectedPapers", user_info.collected_papers_list),
                  path("api/userInfo/searchHistory", user_info.search_history_list),
                  path("api/userInfo/delSearchHistory", user_info.delete_search_history),

                  # 数据管理模块
                  path("api/manage/users", manage.user_list),
                  path("api/manage/papers", manage.paper_list),

                  # 信息检索模块
                  path("api/search/vectorQuery", vector_query),
                  path("api/search/dialogQuery", dialog_query),
                  path("api/search/flush", flush),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
