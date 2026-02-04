#app/utills/utills.py
import json
import chardet
import hashlib
import pandas as pd
import random as rd
from pathlib import Path
from datetime import datetime, timezone,date
from config.config import settings
from config.log_config import logger
from app.bigQuery.bigquery_repository import BigQueryTableRepository
from app.bigQuery.client.client import BigQueryClient

# -------------------------------------------------- #
def get_array(data,value:str = "choices"):
    logger.info(f"Ejecutando get_array" )
    choices,lista_resul = [],[]
    data = json.loads(data)
    try:
        for item in data.get("body", []):
            if item.get("type") == "Input.ChoiceSet":
                choices = item.get(value, [])
                break

                emails = [c["value"] for c in choices]

        for c in choices:
            lista_resul.append(c["value"])

    except Exception as e:
        logger.error(f"Exception : {e}")
        lista_resul.append(str(e))
    
    return lista_resul

# -------------------------------------------------- #
def get_date_time() -> datetime:
    return datetime.now(timezone.utc)

# -------------------------------------------------- #
def get_encoding(ruta:Path):
    logger.info(f"Ejecutando get_encoding" )
    try:
        with open(ruta, "rb") as f:
            result = chardet.detect(f.read(10000))
            encoding = result.get("encoding")

    except Exception as e:
        logger.error(f"Error Enconding : {e}" )
        encoding = "utf-8"

    return str(encoding)

# -------------------------------------------------- #
def chunk_dataframe(df: pd.DataFrame, chunk_size: int):
    logger.info(f"Ejecutando chunk_dataframe" )
    for i in range(0, len(df), chunk_size):
        yield df.iloc[i:i + chunk_size]

# -------------------------------------------------- #
def generar_request_id(destinatario: str) -> str:
    fecha = datetime.now(timezone.utc).date().isoformat()
    raw = f"{destinatario.lower().strip()}" #|{fecha}
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

# -------------------------------------------------- #
def random_mail():    
    correo = rd.choice(["ext_fgonzalezc@Falabella.cl","ext_jcarrion@Falabella.cl"
                    "tmorada@Falabella.cl","migarciab@Falabella.cl"])

    return correo

# -------------------------------------------------- #
def validate_request_id(request_id:list) -> pd.DataFrame:
    logger.info(f"Ejecutando validate_request_id" )
    try:
        lista_request_id = "','".join(request_id)
        
        ambiente   = f"{settings.project_qa}.{settings.bigquery_sandbox_qa}"
        repo = BigQueryTableRepository(table = str("test")
                                    , project_id = str(settings.project_qa)
                                    , client = BigQueryClient().ambientQA())
        query_search = f"""
                select
                case
                when b.submitActionId = 'Enviar' then a.request_id
                when trim(b.submitActionId) = 'Error técnico - Tarjeta no válida o fallo de Teams' 
                and b.Q >3 then a.request_id
                when b.submitActionId is null and a.status_code = 202 then a.request_id
                else "No Aplica" end as request_id
                from `{ambiente}.teams_validation_data` as a
                -------------------------------------
                left join ( 
                        select b.*,c.Q
                        from `{ambiente}.response_validation_data` as b
                        -------------------------------------
                        left join (
                                    select b.request_id,b.submitActionId, count(b.submitActionId) Q
                                    from `{ambiente}.response_validation_data` as b
                                    group by b.request_id,b.submitActionId
                        ) as c on b.request_id = c.request_id
                        -------------------------------------
                        QUALIFY ROW_NUMBER() OVER (PARTITION BY b.request_id ORDER BY b.responseTime DESC) = 1
                        ) as b
                on a.request_id = b.request_id
                where true
                and a.request_id in ('{lista_request_id}')
                and a.request_id not in ('db50679c5fadca53fcf1793b1c0c01b4937c954a77bf16100f954f1634bb559e',
'1e58641b388ec2867f54876235733fb13b845a8ca883dd686384d8c3951d3687',
'1e1b9553c14ad8f6fa6c4bd7d138bdfb24fd33e3f744822e8e32a9726115a4ce',
'2dae0a064f56f45a7e7b4f7f4f2721d8fa11a4e7486e746b0645a208ac4e61ba',
'fc5f6324967f9da30c40babd89428a858eb245453308e0db19e104516ddae3e1',
'a4d567ac2cc99c33aa3b00fea5a19cac7a670271f0e27f6d03f90c5ff557017d',
'1f7c7feeb2bd405cfa16882db467aa6604354df5734a8f261d07347a49525072',
'7d4a5903e355fba929e16df90c6787bfa8d4ebf67d86342fc2ecf6bfd889e063',
'7bd1a68fb7f7001d40acf816de806d8464c8e171c685555f2be4766cc8d4d525',
'bc4c2e83429e487a83d7185126ba27ee7652a9f335a4fe5772944c4fd539f16d',
'8632ceeab96e0a1cbf46be58fd168eb8e9999b2154086bdb3719a08ec83cb701',
'932da4b8e8f3d782538ba29ed298bda11e742b0343bd1350ba2abfcbb9ca1e91',
'c5b8173f090974fd22d5063f8a70f592aaeacf83bdeeff4000dec0713da7df07',
'a77a66b421cf78bdfa66f9bba46b9f2b84824defaaa29ad41566a0ba0913a64a',
'5b65368e3ffec556307fbb296166ac2bb23dcd6181563325abcb27534668b98e',
'55718f30c488ad022d306c30709239edbdc9c009ac0d3409ec310ea332b3cba2',
'da5b2c3a92adaf13fdea4e09e3cbccfe6def8c2c074b88acc04d025ef72ad4f2',
'e7165520d4e0440e0d46523e6f83606d04196fd68906f24a56db8cbfa1314cf8',
'4eb7871922d3ea203ee64d15f148bc4649a2554c3795e1f5910722b0d6d24c6a',
'8415020598d57d2709c7578088fdd28144f0d726401c588d81c3083697610fd7',
'29f5848e35ae5256310a790d0b7f14b02e5b41ebec11ae4471f1572197fb7a2d',
'144bca59d2a0a2783eaf5add2afb6d78ad12d38ec09911299915a81e7f23c4c1',
'fb2805c8fd1256a6992df261bd5fa23832e018fb802743cd1aaf196579e44854',
'76c59e29e8407702a6d44520c580e829a17da530dbfd552a31ec3e7291f6ca14',
'706b4a336db0c46cc21aa4cc9bb667245a60750cfb48fe13961ec85e4c0810dc',
'd7e2bcdfdacc0f1839226323da364dbfeeda0c046cee3ee509de09f3716da366',
'c78161f6028c1dce916a90ac10f9953f9b9026f717dae6adf8c909a51efd584c',
'04fed89ff0be00ac9cceae6c3e75b56025c8fa2c917e42ae9964d10f33075474',
'7c09a45488d21f681da85b2fe4ec1648eb7b7bd8c18a4935464871daaa900f3f',
'6305bfd10f7db890ee439792675b1984523c0eadf01a2a8a8dc9546d43d05c5c',
'f0c9cbf5b683841e5471764da5928af65d0350f186db30e4b9ee2713db2db7fc',
'7d00dabcd313c158378d662e4b1d87424f7e9e76d83247e993e8e3ad2236e907',
'745653ace6af13d0b93e6570ef72126d4a63430c532fde0bbde7cdbd047edd44',
'44b7784288da6874213d38564e2f46e79abcbe11d136367f3c26d8362fadbc46',
'e4b3fd19f06d7f50328c2a6971f7d8d04bd1d01cee00aa0c7c3b564046f672a1',
'a52b93284d4657cccae6b4ea478c90d9a69ee19362bb9ad8c7176e24c5289bd3',
'f13532891908e24273c669ea22b7ddb4c15eb71861a0df0d7777677efb542e36',
'd6adb0010c210b31342e90c5ae776251f876bf2144c10d5f9a8e0c8173dc5be9',
'9567acbe11e0c1a6fe7cc9148b02cfb292bef43d7a826f3eb2609e0ac2b78b0b',
'74c881783a0e5fb3457eac693c29b170ec4fb4a18f136266a5ca0d7eae074165',
'171a3f3503b4ba13bd2fd7d22847bffc684928eef461163ef0901e941c30cdee',
'4e9157061adbfbf29fe9d8682ecbcd2b34083d0aa93702a5bb92cfa317be42d5',
'40a50953076959292280bf61d6d9ef88a8313e639c33f8bae559949cbc91a76e',
'c521f527188b1697db8f67c5d4b488fe57a3acf5ddc203f5bd9002f090361000',
'aaf2af69019dbadd7ecebd806ba87edc68d743c6e779745ed98cd2eb443d99f9',
'15a42ec5b70963ac515977416bde8e3dfe6504a30b19d64990442d664052930d',
'4f2d830474037928de20da8ccb53333a9f576b9d082c551bdd6526227941d89f',
'c73d769783700c23871811ab926c67f5deb4266a43dba6d034d1277276e876ab',
'311a88173b5f310b0f47393ecd49a0201557f222f447bff348b517fb11f66fa7',
'a943949cba4d2f37b73134c25f62bc0d66d132a7af9de4784094997a47dfffd4',
'421fc1d5c14e39eb6999ce3a654cbb129ef5d71ca966500f9685c1fe933066f0',
'87c09fb438f5c3d044dc299f6962e160d8b7b3c7bd8000407fb19d54287422b3',
'446ba60df975bcdb8a0bfc374a7cedbb9108f61a2597c90aa0d1b1ca776bd168',
'0d281642a10b04e9f5218eb4bd1bda0b7459cddb17fa587b71671827101330d1',
'c63e75d1ab9f3512aff0843558ecc6a421fa0a8d7ce93ed03ca11e87d225e6bf',
'c2a2617f2e6924e034e884a42b01a9d7bf93fac9258071a454eb97fb1e4f9606',
'13af57b852b113bc720e4d09e96652436581445efa906db964de4d62952ce129',
'fe2cbb228db40619575b82ff4fe6862c064219dc65784ff2a2daf4f8cbe19d9e',
'190c0cab3b7b56dbf524e97d1e0a6bd3406c2db9522e96f275a8f054aaf976cc',
'2a5cd3e9605d9f326cdb92ecab108f400de46d11afbc2b7822a7b39f2750c5f2',
'e1d6b12b60f56305e5dfa3909f1900fd2e5a6f992ec868bd62d1b4d9ed9d661a',
'f793d19dca61233a0319e238de0e4060777503fc66ea54890a36422b90ca175a',
'b0a37b9ea58bfaf47414323b25b1e269665fb6f717355c1fb1bf26a94f66b045',
'0fb6697b568c2c09819c902a77a64348ed652e4571d2cf3730f44990e56bb945',
'e62efcfad0e4b59e82d80e99ea6d2257b0662686ba2cc36c92fe6fa3b2bd6d04',
'12b74455224fd3d84b9887df966fd788df0120e39881e760536cd2ae18a42181',
'bfd7a806d8e8e06ae67e508d98095b57d9bd3472287ba43dc4d39348ebbcac01',
'a8dd0c173948f4b1804584156a9b61f4c33f60d80cfef36d43382b2440a7b876',
'6cfeea88e022d40558f768e2a252d87f128b5ffdb0967fa9c8b1761a2cf460b8',
'87a7a544471dea454b59d40c5ac3823aecdd65f13bbf3244116c07b0d9487db7',
'6c07af1a93f54bcba63ebc9cf8610dab62246a87b3dbd7d6a1408c008792ee34',
'6eede2d8f3bb4c32f1f731b9c44651cb9938f746e0f602b5f771a6d87150dc19',
'b836e5dd759ba9a3e14a959dd35094e7a61d5413a8cde4fa14c64e2511e02ab7',
'89884a24722a8b10e7c26f51e910dd05fb2ba820e3d749f512501c83ec7829b1',
'ee850ca9fef931f55cc3b5429fc5e37b144d56152bb1a8e3dcdb3a67ad6b5edd',
'efd80e64c64c8fca45198110cfeda1f3485a89f8d5aaf318f92fdd33a7ad70db',
'0231b6fcbeab72d353facc256e1cbd4f11af1b56cbd591210c4a257e7964013d',
'0e486c9cb0ac7814937ce16d78abfab88067becba256d92c67925378265529fb',
'4fccf5c2ebbf1dd3140a91de9c4fb96ffe688950b6919da90968e9d0d550dbb0',
'1f87823b88175a8e4f76eb1c7e9fd73caa2cb5ad69ef221d5d140ff6e1471892',
'15385c0b99b7d191e03fe0b299ec5a277238ef22aea55f0b90e9cb659b5ef604',
'7db07cc8a236ea627b160d426dce77db3c21757522ef64552d8e33360e9e889e',
'8ab7c32f2fbc140f0629ad2533a52bbb51a488f36a65dfc87a4c54c19bf6ff76',
'a59df45373b64c86d7936e080cff9757410f21b8f212b5402c9b78482f56bb1b',
'e5ad68c0724f2540d8b2283a42ab55e7b1de8e22c7b88aa8309d29de424806c4',
'4bc8b3ea19642afc29461b37280419e92623cd68fac44e341566adce3b403d8c',
'308565762502f132d416dc5b76069a15909a4c36a335461c8b6961ae5da22a1b',
'860c59e9e5fa7f673dd0e3dd59e80a2ea7f31de3e2aacee3183756da7a7e81b6',
'7330030ddc86e32ebddcd0663fd8863b4197451fb55448be14295dcb1fa2d89c',
'2a811c7ad3a785afa55cdd39aad51135a28880c01262e3d68566174de34c0192',
'bc8cbba76c64a48ba80eca42248612876270b6669439d3bc38626854d6260a00',
'da18d4584a5d6c4f710f51b948ba4f1ea01696a3f8a18345a3cf1350dd37b97c',
'ea903129b58f9e851efa7fb154505b3f2f41442f03f90a160da0c4d2ead60944',
'ac7ffe6831c649fa623a167cf10f0cc1c3e2ea63481da18fa99f37a19f79897c',
'71a5c01ac6d754cff8d0d78e7d799862050a3ff662516e6cf46dd68127c73147',
'98f8f169f4e90535db9451747577401e65fb85ecde6e992c7135a196679bf00b',
'7e9ed538c5fe6b3b1a178bcd7b4c7d14eb3037c69fb07d02dbadc927dc291192',
'8337f965ae2a4ec259b3469dbce6d642a86dbfcf9934bee7367221e66a1784d0',
'09808c5a8acbad96c8c651caeb7ba83342c83091e448658832f5750a2e1531e1',
'e44c472541157cf162149c46326b03b8b5af014e1141c401a9bf376bf2340f83')

                order by a.timestamp desc"""
        result_query = repo.read_query(query_search)
        return result_query
    
    except Exception as e:
            logger.error(f"Exception : {e}" )
            return pd.DataFrame()


# -------------------------------------------------- #
def reprocess(dfA: pd.DataFrame) -> pd.DataFrame:
    logger.info("Reprocesando %d registros", len(dfA))
    try:
        lista_request = dfA["request_id"].tolist()
        df_ids_b = validate_request_id(lista_request)

        if df_ids_b.empty:
            logger.info("No hay request_id a excluir")
            return dfA

        ids_b = set(df_ids_b["request_id"])

        # se excluyen los datos de ids_b
        dfA_filtrado = dfA[~dfA["request_id"].isin(ids_b)]

        logger.info("Registros finales: %d", len(dfA_filtrado))
        return dfA_filtrado.copy()

    except Exception:
        logger.exception("Error durante reprocesamiento")
        return dfA



