from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError
from rest_framework import generics
from django.views import View
from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import json
import pandas as pd
from .models import(
    CustomUser, 
    Loja, 
    TipoAcesso, 
    TipoServico, 
    CNAE, 
    TipoRegime, 
    RamoAtividade,
    Cliente,
    ClienteExcel,
    DadosReferencia
) 
from .serializers import(
    CustomUserSerializer, 
    TipoServicoSerializer, 
    LojaListViewSimpleSerializer, 
    CNAESelectSerializer, 
    TipoRegimeSerializer, 
    RamoAtividadeSerializer,
    ClienteSerializer,
    ClienteExcelSerializer,
    DadosReferenciaSerializer
)


#LOGIN
class RegisterView(APIView):
    permission_classes = []
    
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = []  # Permitir acesso público

    def post(self, request, *args, **kwargs):
        email    = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class CustomUserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, email, *args, **kwargs):
        user = get_object_or_404(CustomUser, email=email)
        user.delete()
        return JsonResponse({'message': 'Usuário excluído com sucesso!'}, status=200)

    queryset = Loja.objects.all()
    serializer_class = LojaListViewSimpleSerializer
    permission_classes = [IsAuthenticated]
    
#GENERICOS
class CheckCNPJView(View):
    def get(self, request, *args, **kwargs):
        cnpj = request.GET.get('cnpj')
        exists = Loja.objects.filter(cnpj=cnpj).exists()
        return JsonResponse({'exists': exists})

class TipoServicoListView(generics.ListAPIView):
    queryset = TipoServico.objects.all()
    serializer_class = TipoServicoSerializer  
    
class TipoRegimeListView(generics.ListAPIView):
    queryset = TipoRegime.objects.all()
    serializer_class = TipoRegimeSerializer  
    
class RamoAtividadeListView(generics.ListAPIView):
    queryset = RamoAtividade.objects.all()
    serializer_class = RamoAtividadeSerializer  
        
#CNAE
class CNAESelectListView(generics.ListAPIView):
    queryset = CNAE.objects.all()
    serializer_class = CNAESelectSerializer
    permission_classes = []  # Permitir acesso apenas para usuários autenticados
   
#CLIENTES
class ClienteCreateView(generics.CreateAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = []  # Se quiser autenticação
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ClienteListView(generics.ListAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = []  # Se quiser autenticação
  
class UploadExcelView(APIView):
    permission_classes = []
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "Nenhum arquivo fornecido."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtendo o id_cliente da URL
            id_cliente = kwargs.get('id')
            if not id_cliente:
                return Response({"error": "ID do cliente não fornecido."}, status=status.HTTP_400_BAD_REQUEST)
            
            ClienteExcel.objects.filter(id_cliente=id_cliente).delete()
            df = pd.read_excel(file)

            # Remover espaços em branco nos nomes das colunas
            df.columns = df.columns.str.strip()
            # Inspecione as colunas
            #print(df.columns)

            for index, row in df.iterrows():
                # Acesse todas as colunas de forma segura
                cod_prod = row.get('Cód Prod')
                ncm = row.get('NCM')
                descricao_prod = row.get('Descrição Prod')
                cst_icms = row.get('CST ICMS')
                cst_pis = row.get('CST  PIS')
                cst_cofins = row.get('CST COFINS')

                # Verifique se as colunas necessárias estão presentes
                if None in [cod_prod, ncm, descricao_prod, cst_icms, cst_pis, cst_cofins]:
                    return Response({"error": f"Valores ausentes na linha {index}."}, status=status.HTTP_400_BAD_REQUEST)

                obj = ClienteExcel(
                    cfop=0000,
                    cod_prod=cod_prod,
                    ncm=ncm,
                    descricao_banco=descricao_prod,  # Salvando a nova coluna
                    cst_icms=cst_icms,
                    cst_pis=cst_pis,
                    cst_cofins=cst_cofins,
                    id_cliente=id_cliente
                )
                obj.save()  # Salvar no banco de dados

            
            # Recuperar os dados inseridos
            dados_inseridos = ClienteExcel.objects.filter(id_cliente=id_cliente).values()
            return Response({"message": "Dados inseridos com sucesso!", "dados": list(dados_inseridos)}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class CorrigirDadosView(APIView):
    def post(self, request, *args, **kwargs):
        cliente_dados = ClienteExcel.objects.all()
        for cliente in cliente_dados:
            try:
                referencia = DadosReferencia.objects.get(ncm=cliente.ncm)
                cliente.cst_icms = referencia.cst_icms
                cliente.cst_pis = referencia.cst_pis
                cliente.cst_cofins = referencia.cst_cofins
                cliente.reducao = referencia.reducao
                cliente.save()
            except DadosReferencia.DoesNotExist:
                pass

        return Response({'message': 'Data corrected'}, status=status.HTTP_200_OK)
    
class UploadBaseExcelView(APIView):
    permission_classes = []
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "Nenhum arquivo fornecido."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            DadosReferencia.objects.all().delete()
            df = pd.read_excel(file)

            # Remover espaços em branco e duplicados nos nomes das colunas
            df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

            # Remover linhas completamente vazias
            df.dropna(how='all', inplace=True)

            # Verifique o tamanho do DataFrame
            total_rows = len(df)

            # Forçar 'CODIGO SEM PONTO' como int, preenchendo valores nulos com 0
            df['CODIGO SEM PONTO'] = df['CODIGO SEM PONTO'].fillna(0).astype('Int64')

            # Defina o tamanho do lote
            batch_size = 300  # Ajuste conforme a capacidade da sua instância

            # Processar em lotes
            for start in range(0, total_rows, batch_size):
                end = min(start + batch_size, total_rows)
                batch_df = df.iloc[start:end]

                batch_objects = []
                
                for index, row in batch_df.iterrows():
                    #print(f"Processando lote: {start} - {end}, Linha: {index}")
                    
                    tipo                 = row.get('TIPO')
                    codigo_original_tipi = row.get('CODIGO ORIGINAL TIPI')
                    codigo_sem_ponto     = row.get('CODIGO SEM PONTO')
                    descricao_tipi       = row.get('DESCRIÇÃO TIPI')
                    ipi                  = row.get('IPI')
                    cst_pis              = row.get('CST PIS')
                    cst_cofins           = row.get('CST COFINS')
                    cst_icms_sp          = row.get('CST ICMS SP')
                    cst_icms_rj          = row.get('CST ICMS RJ')
                    cst_icms_es          = row.get('CST ICMS ES')
                    cst_icms_mg          = row.get('CST ICMS MG')
                    etc                  = row.get('ETC')
                    reducao              = 0

                    # Verifique se as colunas necessárias estão presentes
                    if None in [codigo_sem_ponto, descricao_tipi, cst_icms_sp, cst_pis, cst_cofins, ipi]:
                        #print(f"Valores ausentes na linha {index}")
                        return Response({"error": f"Valores ausentes na linha {index}."}, status=status.HTTP_400_BAD_REQUEST)
                   
                    # Verifique se descricao_tipi é uma string e limite o tamanho
                    if isinstance(descricao_tipi, str) and len(descricao_tipi) > 254:
                        descricao_tipi = descricao_tipi[:254]

                    # Adicionar a instância do modelo na lista para o lote
                    obj = DadosReferencia(
                        tipo=tipo,
                        codigo_original_tipi=codigo_original_tipi,
                        codigo_sem_ponto=codigo_sem_ponto,
                        descricao_tipi=descricao_tipi,
                        ipi=ipi,
                        cst_pis=cst_pis,
                        cst_cofins=cst_cofins,
                        cst_icms_sp=cst_icms_sp,
                        cst_icms_rj=cst_icms_rj,
                        cst_icms_es=cst_icms_es,
                        cst_icms_mg=cst_icms_mg,
                        etc=etc,
                        reducao=reducao
                    )
                    batch_objects.append(obj)

                # Salvar o lote no banco de dados
                DadosReferencia.objects.bulk_create(batch_objects)
                #print(f"Lote {start} - {end} salvo com sucesso.")

            return Response({"message": "Dados inseridos com sucesso no banco de dados!"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



        
class CompareDadosView(APIView):
    """
    Atualiza os dados de todas as linhas de ClienteExcel com base nos dados de DadosReferencia
    pelo id_cliente fornecido na requisição e verifica os campos cst_icms, cst_pis e cst_cofins.
    """

    def post(self, request, *args, **kwargs):
        # Pegar o id_cliente fornecido na requisição
        id_cliente = kwargs.get('id')

        if not id_cliente:
            return Response({"error": "id_cliente não fornecido."}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar todas as linhas do ClienteExcel para o id_cliente fornecido
        clientes = ClienteExcel.objects.filter(id_cliente=id_cliente)
        
        if not clientes.exists():
            return Response({"error": "Nenhum cliente encontrado com este id_cliente."}, status=status.HTTP_404_NOT_FOUND)
        
        atualizados = []
        nao_atualizados = []

        # Iterar por cada linha do cliente
        for cliente in clientes:
            try:
                # Buscar na tabela DadosReferencia com base no NCM (codigo_sem_ponto)
                referencias = DadosReferencia.objects.filter(codigo_sem_ponto=cliente.ncm)

                if referencias.exists():
                    # Pega o primeiro registro da lista (ou trate como quiser)
                    referencia = referencias.first()  

                    # Verificar se há diferenças nos campos de cst_icms, cst_pis e cst_cofins
                    atualizado = False
                    if cliente.cst_icms != referencia.cst_icms_sp:
                        cliente.cst_icms = referencia.cst_icms_sp
                        atualizado = True
                    if cliente.cst_pis != referencia.cst_pis:
                        cliente.cst_pis = referencia.cst_pis
                        atualizado = True
                    if cliente.cst_cofins != referencia.cst_cofins:
                        cliente.cst_cofins = referencia.cst_cofins
                        atualizado = True

                    # Atualizar no banco se houver mudanças
                    if atualizado:
                        cliente.save()
                        atualizados.append({
                            "cod_prod": cliente.cod_prod,
                            "ncm": cliente.ncm,
                            "cst_icms": cliente.cst_icms,
                            "cst_pis": cliente.cst_pis,
                            "cst_cofins": cliente.cst_cofins
                        })
                    else:
                        nao_atualizados.append({
                            "cod_prod": cliente.cod_prod,
                            "ncm": cliente.ncm,
                            "mensagem": "Já está atualizado"
                        })
                else:
                    nao_atualizados.append({
                        "cod_prod": cliente.cod_prod,
                        "ncm": cliente.ncm,
                        "mensagem": "Referência de dados não encontrada"
                    })

            except Exception as e:
                nao_atualizados.append({
                    "cod_prod": cliente.cod_prod,
                    "ncm": cliente.ncm,
                    "mensagem": str(e)  # Retorna a mensagem do erro
                })

        # Retornar a lista de itens atualizados e não atualizados
        return Response({
            "atualizados": atualizados,
            "nao_atualizados": nao_atualizados
        }, status=status.HTTP_200_OK)
          
class ClienteExcelDetailView(APIView):

    def get(self, request, *args, **kwargs):
        # Pegar o id_cliente fornecido na requisição
        id_cliente = kwargs.get('id')

        try:
            clientes = ClienteExcel.objects.filter(id_cliente=id_cliente)  # Filtra pelos registros
            if not clientes.exists():
                return Response({"error": "Nenhum cliente encontrado com este id_cliente."}, status=status.HTTP_404_NOT_FOUND)

            serializer = ClienteExcelSerializer(clientes, many=True)  # Serializa os dados
            return Response(serializer.data, status=status.HTTP_200_OK)  # Retorna os dados serializados

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AtualizarClienteView(APIView): 
    """
    Atualiza os campos modificados para múltiplos clientes.
    """
    def put(self, request, *args, **kwargs):
        try:
            # Converte o corpo da requisição em um objeto JSON
            body = json.loads(request.body)

            # "alteracoes" é a lista de clientes com suas respectivas alterações
            alteracoes = body.get('alteracoes', [])

            if not alteracoes:
                return JsonResponse({'message': 'Nenhuma alteração fornecida.'}, status=400)

            # Itera sobre a lista de alterações
            for alteracao in alteracoes:
                # Busca o cliente correspondente no banco de dados
                id = alteracao.get('id')
                try:
                    cliente = ClienteExcel.objects.get(id=id)
                except ClienteExcel.DoesNotExist:
                    return JsonResponse({'error': f'Cliente com id_cliente {id} não encontrado.'}, status=404)

                # Atualiza os campos alterados
                cliente.cfop = alteracao.get('cfop', cliente.cfop)
                cliente.cod_prod = alteracao.get('cod_prod', cliente.cod_prod)
                cliente.ncm = alteracao.get('ncm', cliente.ncm)
                cliente.descricao_banco = alteracao.get('descricao_banco', cliente.descricao_banco)
                cliente.cst_icms = alteracao.get('cst_icms', cliente.cst_icms)
                cliente.cst_pis = alteracao.get('cst_pis', cliente.cst_pis)
                cliente.cst_cofins = alteracao.get('cst_cofins', cliente.cst_cofins)

                # Salva as alterações no banco de dados
                cliente.save()

            return JsonResponse({'message': 'Clientes atualizados com sucesso!'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Erro ao decodificar JSON.'}, status=400)

        return JsonResponse({'error': 'Método não permitido.'}, status=405)
    
class DownloadExcelView(APIView):
    """
    Gera e faz o download de um arquivo Excel com os dados dos clientes filtrados por id_cliente.
    """
    def get(self, request, id, *args, **kwargs):
        # Busca os clientes filtrando pelo id_cliente
        clientes = ClienteExcel.objects.filter(id_cliente=id).values(
            'cfop', 'cod_prod', 'ncm', 'descricao_banco', 'cst_icms', 'cst_pis', 'cst_cofins'
        )

        # Verifica se foram encontrados dados
        if not clientes:
            return Response({'error': 'Nenhum cliente encontrado para o id_cliente fornecido.'}, status=404)

        # Cria um DataFrame do pandas a partir dos dados
        df = pd.DataFrame(clientes)

        # Cria um objeto HttpResponse para o arquivo Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=clientes_{id}.xlsx'

        # Usa ExcelWriter para escrever no response
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Clientes')

        return response