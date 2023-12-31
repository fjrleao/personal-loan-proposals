from rest_framework.views import APIView, Request, Response, status

from .serializers import PersonalLoanSerializer
from .models import PersonalLoan
from .tasks import analyse_loan_proposals

from person.serializers import PersonSerializer
from person.models import Person


class PersonalLoanProposalView(APIView):

    def post(self, request: Request) -> Response:
        serializer_person = PersonSerializer(data=request.data)
        serializer_loan_value = PersonalLoanSerializer(data=request.data)

        if not serializer_person.is_valid():
            return Response(serializer_person.errors, status=status.HTTP_400_BAD_REQUEST)

        if not serializer_loan_value.is_valid():
            return Response(serializer_loan_value.errors, status=status.HTTP_400_BAD_REQUEST)

        ## Bloco try/catch para procurar os dados de uma pessoa, caso ela não tenha cadastro, o cadastro será criado.
        try:
            person = Person.objects.get(
                cpf=serializer_person.validated_data['cpf']
            )
        except:
            person = Person.objects.create(**serializer_person.validated_data)

        personal_loan = PersonalLoan.objects.create(
            **serializer_loan_value.validated_data, person_id=person.id
        )

        analyse_loan_proposals.delay(personal_loan.id)

        return Response(data={
            'message': 'Loan proposal under review'
        }, status=status.HTTP_200_OK)
