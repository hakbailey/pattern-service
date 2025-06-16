from ansible_base.lib.utils.views.ansible_base import AnsibleBaseView
from rest_framework.viewsets import ModelViewSet

from .models import Automation
from .models import ControllerLabel
from .models import Pattern
from .models import PatternInstance
from .serializers import AutomationSerializer
from .serializers import ControllerLabelSerializer
from .serializers import PatternInstanceSerializer
from .serializers import PatternSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response


class CoreViewSet(AnsibleBaseView):
    pass


class PatternViewSet(CoreViewSet, ModelViewSet):
    queryset = Pattern.objects.all()
    serializer_class = PatternSerializer


class ControllerLabelViewSet(CoreViewSet, ModelViewSet):
    queryset = ControllerLabel.objects.all()
    serializer_class = ControllerLabelSerializer


class PatternInstanceViewSet(CoreViewSet, ModelViewSet):
    queryset = PatternInstance.objects.all()
    serializer_class = PatternInstanceSerializer


class AutomationViewSet(CoreViewSet, ModelViewSet):
    queryset = Automation.objects.all()
    serializer_class = AutomationSerializer


@api_view(["GET"])
def ping(request):
    return Response(data={"status": "ok"}, status=200)


@api_view(["GET"])
def test(request):
    return Response(data={"hello": "world"}, status=200)
