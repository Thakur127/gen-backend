from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from gen.permissions import IsOwnerOnly
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
import stripe

from course.models import Course
from course.models import Enroll
from course.models import AvailableCurrency

from .models import Payment
from .serializers import PaymentSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY
User = get_user_model()


class Currency(APIView):
    def get(self, request, format=None):
        currencies = []
        for code, label in AvailableCurrency.choices:
            currencies.append({"code": code, "label": label})

        return Response(currencies)


class StripeConfig(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        return Response(data={"publicKey": settings.STRIPE_PUBLISHABLE_KEY})


class CreateCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        course_id = request.data.get("course_id")
        course = Course.objects.filter(pk=course_id).first()
        if not course:
            return Response(
                data={"error": "Data not found."}, status=status.HTTP_400_BAD_REQUEST
            )

        if Enroll.objects.filter(course=course, student=request.user).first():
            return Response(
                {"error": f"Already Enrolled in the course."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        domain_url = (
            settings.FRONTEND_DOMAIN
            if settings.FRONTEND_DOMAIN
            else "http://localhost:5173"
        )
        info_query = f"course_name={course.title}&course_id={course.pk}&amount={course.price}&currency={course.currency}"

        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url
                + "/payment/completed?status=success&session_id={CHECKOUT_SESSION_ID}"
                + "&"
                + info_query,
                cancel_url=domain_url
                + "/payment/completed?status=failed"
                + "&"
                + info_query,
                payment_method_types=["card"],
                mode="payment",
                line_items=[
                    {
                        "price_data": {
                            "currency": course.currency,
                            "product_data": {
                                "name": course.title,
                                "description": course.description,
                                "images": [course.cover_img],
                            },
                            "unit_amount": int(course.price * 100),
                        },
                        "quantity": 1,
                    }
                ],
                metadata={"course_id": course.pk, "user_id": request.user.pk},
            )
        except Exception as e:
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # return HttpResponseRedirect(checkout_session.url)
            return Response(
                data={
                    "sessionId": checkout_session["id"],
                    "sessionUrl": checkout_session.url,
                }
            )


class WebhookView(APIView):
    def post(self, request, format=None):
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        stripe_webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, stripe_webhook_secret
            )
        except ValueError as e:
            print(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except stripe.error.SignatureVerificationError as e:
            print(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if event.type == "payment_intent.payment_failed":
            payment_intent = event.data.object

            # Extract necessary information from the payment_intent object
            transaction_id = payment_intent.id
            session_id = payment_intent.metadata.get("session_id")
            amount = payment_intent.amount / 100  # Convert from cents to currency
            currency = payment_intent.currency
            course_id = payment_intent.metadata.get("course_id")
            user_id = payment_intent.metadata.get("user_id")

            user = User.objects.filter(pk=user_id).first()
            course = Course.objects.filter(pk=course_id).first()

            if course and user:
                Payment.objects.create(
                    transaction_id=transaction_id,
                    session_id=session_id,
                    amount=amount,
                    currency=currency,
                    status="failed",  # Set the status to "failed" for payment failed event
                    course=course,
                    user=user,
                )

        if event.type == "checkout.session.completed":
            session = event.data.object
            print(session)

            transaction_id = session.get("payment_intent")
            session_id = session.get("id")
            currency = session.get("currency").upper()
            amount = session.get("amount_total") / 100
            payment_status = session.get("payment_status")
            course_id = session.metadata.get("course_id")
            user_id = session.metadata.get("user_id")

            if course_id and user_id:
                course = Course.objects.filter(pk=course_id).first()
                user = User.objects.filter(pk=user_id).first()

                if course and user:
                    new_enrollment = Enroll.objects.create(
                        student=user,
                        course=course,
                    )
                    Payment.objects.create(
                        transaction_id=transaction_id,
                        session_id=session_id,
                        currency=currency,
                        amount=amount,
                        payment_status=payment_status,
                        enrollment=new_enrollment,
                        user=user,
                        course=course,
                    )

                return Response(
                    {"detail": "Enrollment Successful."}, status=status.HTTP_201_CREATED
                )

        return Response(status=status.HTTP_400_BAD_REQUEST)


class PaymentsView(ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class PaymentDetailView(RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsOwnerOnly]
    queryset = Payment.objects.all
    lookup_field = "transaction_id"

    def get_object(self):
        transaction_id = self.kwargs.get("transaction_id")
        return Payment.objects.filter(transaction_id=transaction_id).filter()

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
