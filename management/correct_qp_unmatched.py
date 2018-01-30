from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import datetime
import sys

class Command(BaseCommand):
    help = 'Fixes unmatched MPs during Question Period study period (1975-)'
        
    def handle(self, *args, **options):

        correctiondict = {"Mr. Garth  Ihrner@Halton-Peel":"8935b46b-8d54-41eb-b32b-07568b4005a1",
                           "Hon.   J.-J. Blais@Solicitor General":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Mr.   TUmer@Vancouver Quadra":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Mr.   C.-A. Gauthier@Roberval":"6ef85d82-0243-4e17-a3bd-41a064680fd1",
                           "Right Hon. John N. Dirner@Leader of the Opposition":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Right Hon.  P. E.@Prime Minister":"3e66b4c9-6dae-4083-8d96-5d3f94979e94",
                           "Hon.   Jack. H. Horner@Minister of Industry, Trade and Commerce":"00163189-b2e2-4300-9100-81f7d68a7930",
                           "Mr.   Ed. Lumley@Stormont-Dundas":"7beeed73-0eef-4875-ac4f-eae4a5b16956",
                           "Hon.   C'has. L. C'accia@Davenport":"328b9cb9-24ea-4602-abb8-ff33227c2f3f",
                           "Mr.   Wm. Andres@Parliamentary Secretary to Minister of State (Multicuituralism":"f5130852-726b-4537-b4b3-400e85bc27fd",
                           "Hon. Otto E. Fang@Minister of Transport":"c97a5dad-3c56-4861-9d78-991bb0107b29",
                           "Mr. Walter Van  de Walle@St. Albert":"c07e4f86-a8d4-4d58-8692-23d19fc34e34",
                           "Mr.   GabyLarrivee@Joliette":"76e93b39-13b4-49ff-985f-98cb32b46727",
                           "Hon. Jake  F.pp@Minister of Indian Affairs and Northern Development":"a59b2ec7-63a6-4ab2-adc9-53f2dea03531",
                           "Hon.   Gerald. S. Merrithew@for the Minister of State (Finance":"6c9f707c-dce0-468f-bf83-5a7c49f617db",
                           "Hon.   Otto. E. Lang@Minister of Transport":"c97a5dad-3c56-4861-9d78-991bb0107b29",
                           "Ms.   Blondin@":"48d581ee-d2d4-46ff-9f50-6934e122298f",
                           "Right Hon. John N. Ibrner@Leader of the Opposition":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Hon.   Chas. L. Caccia@Minister of Labour":"328b9cb9-24ea-4602-abb8-ff33227c2f3f",
                           "Mr. Garth  Itirner@Halton-Peel":"8935b46b-8d54-41eb-b32b-07568b4005a1",
                           "Mr. Garth  Dimer@Halton-Peel":"8935b46b-8d54-41eb-b32b-07568b4005a1",
                           "Hon.   Ed. Lumley@Minister of Industry, Trade and Commerce and Minister of Regional Economic Expansion":"7beeed73-0eef-4875-ac4f-eae4a5b16956",
                           "Mr.   J.-J. Blais@Parliamentary Secretary to President of the Treasury Board":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Mr. Jesse P. Elis@Parliamentary Secretary to Minister of Transport":"573c0758-57bf-4bcb-8ccf-b10290b5e0c9",
                           "Mr.   John. M. Reid@Parliamentary Secretary to President of the Privy Council":"8cd6c785-293e-4f33-8d82-a119256eca2d",
                           "Mr.   Wdson@Etobicoke Centre":"93108f92-7ed6-4601-8610-a5aa10516fb9",
                           "Mr. Robert E. Ske@":"a10911a7-55dd-4bb3-8f27-a1f6534327ed",
                           "Mr.  R. Gordon. L. Fairweather@Fundy-Royal":"f320ac0c-d005-4580-8424-bd9524e95491",
                           "Mr.   J.-J. Blais@Parliamentary Secretary to President of Privy Council":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Hon.   Paul. J. Cosgrove@Minister of State (Finance":"1cc428d6-4a0f-4d4a-a9d4-ac69e472f9cd",
                           "Mr.   Jacques-L. Trudel@Montreal-Bourassa":"f8413e83-dbad-49d1-b0c4-9ffc000588a3",
                           "Mr. Mac  Eachen@":"29120c21-7fca-48fe-bd93-53ba86e83429",
                           "Hon.   J.-J. Blais@for Mr. Lalonde":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Mr.   Wm. Andres@Lincoln":"f5130852-726b-4537-b4b3-400e85bc27fd",
                           "Mr.   Rirner@Vancouver Quadra":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Mr.   C'has. L. Caccia@Davenport":"328b9cb9-24ea-4602-abb8-ff33227c2f3f",
                           "Mr.   John. R. Rodriguez@Nickel Belt":"b8d398f6-0459-4cd1-9369-c5cb5c1d7dd6",
                           "Mr. Bob  Homer@Mississauga West":"cc2c8f8f-350d-43b1-80ad-a97265cd7700",
                           "Hon.   J.-J. Blais@for the President of the Privy Council":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Right Hon.   P.E. Trudeau@Prime Minister":"3e66b4c9-6dae-4083-8d96-5d3f94979e94",
                           "Mr.   Dirner@Halton -Peel":"8935b46b-8d54-41eb-b32b-07568b4005a1",
                           "Mr.   Ttorner@Vancouver Quadra":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Hon.   Jacques-L. Trudel@Parliamentary Secretary to Minister of Finance":"f8413e83-dbad-49d1-b0c4-9ffc000588a3",
                           "Mr. Walter Van  De Walle@Pembina":"c07e4f86-a8d4-4d58-8692-23d19fc34e34",
                           "Mr. Bob  Weiunan@Fraser Valley West":"a3e7d649-bca5-467e-93b1-86911b50a1ca",
                           "Hon. Andre  Harvie@Minister of State and Leader of the government in the House of Commons":"fbce8351-5fec-45a8-9b6b-2514fa79811a",
                           "Mr.   Timer@Vancouver Quadra":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Mr. Van  De Walle@":"c07e4f86-a8d4-4d58-8692-23d19fc34e34",
                           "Mr.   Tbmer@Vancouver Quadra":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Mr.   Heward. Grafftey@Brome-Missisquoi":"95d80bc3-ef90-4b95-aa06-66756301e54b",
                           "Hon.   Allan. J. MacEachen@President of the Privy Council":"29120c21-7fca-48fe-bd93-53ba86e83429",
                           "Mr.   Tiiraer@Vancouver Quadra":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Mr. Garth  Ibmer@Halton-Peel":"8935b46b-8d54-41eb-b32b-07568b4005a1",
                           "Hon.   J.-J. Blais@for the Minister of Finance":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Right Hon.   John. N. Turner@Leader of the Opposition":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Mr.   Jacques-L. Trudel@Parliamentary Secretary to the President of the Treasury Board":"f8413e83-dbad-49d1-b0c4-9ffc000588a3",
                           "Hon.   Allan. J. MacEachen@Deputy Prime Minister and Secretary of State for External Affairs":"29120c21-7fca-48fe-bd93-53ba86e83429",
                           "Hon.   Andre. Ouellet@Papineau - Saint-Michel":"8eed4f27-aee9-4796-b78e-b81a57c98ee8",
                           "Mr.   Ronald. J. Duhamel@St. Boniface":"3c3a67cc-b4f6-4d09-a652-c15faeb264a4",
                           "Mr. Bob  Homer@Mississauga North":"cc2c8f8f-350d-43b1-80ad-a97265cd7700",
                           "Mr.   Jacques-L. Trudel@Parliamentary. Secretary to Minister of Finance":"f8413e83-dbad-49d1-b0c4-9ffc000588a3",
                           "Mr. Kenneth Albert  Janies@Parliamentary Secretary to the Minister of Supply and Services":"9117937f-b7bc-4454-8914-ddeecf186989",
                           "Mr.   Jacques-L. Trudel@Parliamentary Secretary to President of the Treasury Board":"f8413e83-dbad-49d1-b0c4-9ffc000588a3",
                           "Mr. Simon  de Jdtig@Regina East":"5fd68b94-0c72-4ac3-a336-e9302792c3c8",
                           "Mr. Rod  Biaker@Lachine":"8b173462-ff95-47f1-a93e-a813c66ddd7b",
                           "Mr. Ken  Janies@Parliamentary Secretary to Minister of Supply and Services":"9117937f-b7bc-4454-8914-ddeecf186989",
                           "Hon.   Chas. L. Caccia@":"328b9cb9-24ea-4602-abb8-ff33227c2f3f",
                           "Mr.   Don. Boudria@Glengarry-Prescott-Russell":"efec68a7-e1fd-490f-8b6a-95313440440c",
                           "Mr.   J.W. Bud Bird@Fredericton-York Sunbury":"27d54edd-ee41-4a52-8c15-ec7dbb61ebf9",
                           "Mr.   J.W. Bud Bird@Fredericton- York-Sunbury":"27d54edd-ee41-4a52-8c15-ec7dbb61ebf9",
                           "Mr.   de Jong@":"5fd68b94-0c72-4ac3-a336-e9302792c3c8",
                           "Mr.  J. H. Homer@Crowfoot":"00163189-b2e2-4300-9100-81f7d68a7930",
                           "Mr. Garth  Tinier@Halton-Peel":"8935b46b-8d54-41eb-b32b-07568b4005a1",
                           "Mr.   Dimer@Vancouver Quadra":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Mr.   de Cotret@":"c75110fb-d23c-4a3b-ad31-aa3a6d824332",
                           "Mr. Garth  Dirner@Halton-Peel":"8935b46b-8d54-41eb-b32b-07568b4005a1",
                           "Mrs.   Blondin@":"48d581ee-d2d4-46ff-9f50-6934e122298f",
                           "Ms.   Duplessis@":"9719b2ad-0b43-492e-9f96-307ba571fed9",
                           "Mr.   Bob. Kaplan@Parliamentary Secretary to Minister of National Health and Welfare":"8c4715f2-2a10-48a2-bbeb-b3f407c4df4b",
                           "Hon.   Ron. Basford@Minister of Justice":"eacdf906-7476-407d-a168-5a63fea9ab46",
                           "Hon.   Chas. L. Caecia@Davenport":"328b9cb9-24ea-4602-abb8-ff33227c2f3f",
                           "Hon.   J.-J. Blais@Nipissing":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Mr.   Timer@Halton-Peel":"8935b46b-8d54-41eb-b32b-07568b4005a1",
                           "Mr.   Ed. Lumley@Parliament Secretary to Minister of Regional Economic Expansion":"7beeed73-0eef-4875-ac4f-eae4a5b16956",
                           "Hon.   Eril. Nielsen@Deputy Prime Minister and Minister of National Defence":"8c857bdf-3db5-43c3-8ee0-d33d66a80817",
                           "Right Hon. John N. Tbmer@Leader of the Opposition":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Mr. Raymond  Gameau@Laval-des-Rapides":"4483e59c-3fa5-4c2f-802e-c36ece2fb12f",
                           "Mr.   Jacques-L. Trudel@Parliamentary Secretary to Minister of Finance":"f8413e83-dbad-49d1-b0c4-9ffc000588a3",
                           "Mr.   J.-J. Blais@Nipissing":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Hon.   J.-J. Blais@for President of the Treasury Board":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Mr.   Jean-R. Roy@Timmins":"541ffd0f-bcbe-4080-9246-c878318b1e88",
                           "Mr.   Frith. Mr. Frith@":"822034f9-5ebc-445e-9b04-b00a22eda394",
                           "Hon.   J.-J. Blais@Acting Minister of Justice":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Mr.   Dimer@Halton-Peel":"8935b46b-8d54-41eb-b32b-07568b4005a1",
                           "Mr. Nelson A. Riss@Kamloops-Shuswap":"65f64341-6e0c-46ae-8714-7a9e85e191fa",
                           "Hon.   J.-J. Blais@Minister of Supply and Services":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Hon. Stewart  Mclnnis@Minister of Public Works":"c791da1c-713d-4682-8ac4-2c580c6f28b4",
                           "The Right Hon. Prime  Minister.Mr. Mulroney@":"1335c5d9-2c4e-4ed4-b8d2-c85f1099e8d8",
                           "Mr.   Jacques-L. Trudel@Parliamentary Secretary to President of Treasury Board":"f8413e83-dbad-49d1-b0c4-9ffc000588a3",
                           "Mr.   J.-J. Blais@Parliamentary Secretary to President of the Privy Coucil":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Mr. Walter Van  De Waile@Pembina":"c07e4f86-a8d4-4d58-8692-23d19fc34e34",
                           "Mr. Garth  Ibrner@Halton-Peel":"8935b46b-8d54-41eb-b32b-07568b4005a1",
                           "Mrs. Monique  Bernatchez-Tardif@Parliamentary Secretary to Minister of Regional Industrial Expansion":"68ba5d75-52a4-4ab5-9eff-bcd1281c4007",
                           "Hon. Jake  F.pp@Provencher":"a59b2ec7-63a6-4ab2-adc9-53f2dea03531",
                           "Mr.   Wm. Andres@Parliamentary Secretary to Minister of State (Multiculturalism":"f5130852-726b-4537-b4b3-400e85bc27fd",
                           "Mr.   James. A. McGrath@St. John's East":"c66cf26a-e903-46cf-9b31-057ed4080f6c",
                           "Mr.   J.W. Bud@Fredericton-York-Sunbury":"27d54edd-ee41-4a52-8c15-ec7dbb61ebf9",
                           "Mr.   Tinner@Vancouver Quadra":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "The Hon. Government  Whip.Mr. Fennell@":"5f1b1598-eccb-4311-824c-051698d34046",
                           "Mr. Mac  Flarb@Ottawa Centre":"4f96c1bc-512c-4a39-b653-da4a175e6426",
                           "Mr.   J.-J. Blais@Parliamentary Secretary to President of the Privy Council":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Mrs.   Duplessis@":"9719b2ad-0b43-492e-9f96-307ba571fed9",
                           "Hon.   Andre. Ouellet@Papineau":"8eed4f27-aee9-4796-b78e-b81a57c98ee8",
                           "Mr. Garth  Timer@Halton-Peel":"8935b46b-8d54-41eb-b32b-07568b4005a1",
                           "Mr.   Joe. Fontana@London East":"271b9d41-1d28-4ac0-8a43-39773260f1a0",
                           "Hon.   Gerald. S. Merrithew@Minister of State (Forestry and Mines":"6c9f707c-dce0-468f-bf83-5a7c49f617db",
                           "Hon.   Flora@":"a5991092-dfe7-49e8-af99-874d3a54d86b",
                           "Hon. Jean-Pierre  Coyer@Minister of Supply and Services":"624d6776-49f8-4aa4-bf1e-1f8a04735afc",
                           "Right Hon. John N. Ttorner@Leader of the Opposition":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Hon. Ron  Bastard@Minister of Justice":"eacdf906-7476-407d-a168-5a63fea9ab46",
                           "Hon. Barbara  MlcDougall@Secretary of State for External Affairs":"0a78b8e5-2f53-46d3-a718-64365a688117",
                           "Mr.  R. Gordon L. Fairweather@Fundy-Royal":"f320ac0c-d005-4580-8424-bd9524e95491",
                           "Mr. Albert  Bichard@Bonaventure-iles-de-la-Madeleine":"806fe861-7408-463e-af2c-c1bf3cc31ce3",
                           "Mr.   J.-J. Blais@Parliamentary Secretary to the President of the Privy Council":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Mr.   J.J. Blais@Nipissing":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Mr.   Ed. Lumley@Parliamentary Secretary to Minister of Regional Economic Expansion":"7beeed73-0eef-4875-ac4f-eae4a5b16956",
                           "Mr.   Elmer. M. MacKay@Central Nova":"9bc870a5-bc5d-4b05-ac22-779f048d206c",
                           "Mr. Albert  Bichard@Bonaventure-Iles-de-la-Madeleine":"806fe861-7408-463e-af2c-c1bf3cc31ce3",
                           "Right Hon. John N. Rirner@Leader of the Opposition":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Right Hon. John N. Ihrner@Leader of the Opposition":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Mr.   J.W. Bud Bird@Fredericton-York- Sunbury":"27d54edd-ee41-4a52-8c15-ec7dbb61ebf9",
                           "Hon.   Herb. Gray@Windsor West":"4e3a9e68-a6fb-4e24-9458-cfe2e836c8bc",
                           "Mr.   J.W. Bud Bird@Fredericton-York-Sunbury":"27d54edd-ee41-4a52-8c15-ec7dbb61ebf9",
                           "Mr. Ken  Janies@Sarnia-Lambton":"9117937f-b7bc-4454-8914-ddeecf186989",
                           "Right Hon.   P- E. Trudeau@Prime Minister":"3e66b4c9-6dae-4083-8d96-5d3f94979e94",
                           "Ms.   Ethel@":"48d581ee-d2d4-46ff-9f50-6934e122298f",
                           "Mr.   Itirner@Halton-Peel":"8935b46b-8d54-41eb-b32b-07568b4005a1",
                           "Right Hon. John N. Dimer@Leader of the Opposition":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Mr. Nelson A. Rlis@Kamloops-Shuswap":"65f64341-6e0c-46ae-8714-7a9e85e191fa",
                           "Mr. Jean  Robert-Gauthier@Ottawa-Vanier":"26223e14-510e-4dcb-8a95-e4483fb87b9e",
                           "Mr.   J.-J. Blais@Postmaster General":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Mr. Albert  Becliard@Bonaventure-Iles-de-la-Madeleine":"806fe861-7408-463e-af2c-c1bf3cc31ce3",
                           "Mrs. Diane  Marieau@Sudbury":"914c8d01-d551-4b0a-bf37-47dcd2744210",
                           "Mr. Stewart  Mclnnis@Halifax":"c791da1c-713d-4682-8ac4-2c580c6f28b4",
                           "Mr. Lyle Dean Mac  William@Okanagan -Shuswap":"9c8ce4b0-87b5-4ab6-9645-c4e81555e158",
                           "Mr. Garth  Uirner@Halton-Peel":"8935b46b-8d54-41eb-b32b-07568b4005a1",
                           "Mr. David  Bjomson@Selkirk-Red River":"62ced82d-e217-476b-93bd-0d457e6742d3",
                           "Mr. Bill  Doram@Peterborough":"b8477412-c099-4b2b-89a8-94155dd3d914",
                           "Mr.   J.J. Blais@Parliamentary Secretary to President of the Privy Council":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Mr.   Eld. Lumley@Parliamentary Secretary to Minister of Regional Economic Expansion":"7beeed73-0eef-4875-ac4f-eae4a5b16956",
                           "Mr. Walter Van  De Walle@St. Albert":"c07e4f86-a8d4-4d58-8692-23d19fc34e34",
                           "Hon.   Chas. L. Caccia@Davenport":"328b9cb9-24ea-4602-abb8-ff33227c2f3f",
                           "Mr.   Thraer@Vancouver Quadra":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Mr.   J.-J. Blais@for Mr. Breau":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Mr.   Len. Gustafson@Assiniboia":"80fb46d2-7ead-422d-a70f-585c8ff50372",
                           "Hon. Jack H. Homer@Minister of Industry, Trade and Commerce":"00163189-b2e2-4300-9100-81f7d68a7930",
                           "Mr.   Ed. Lumley@Parliamentary Secretary to Minister of Finance":"7beeed73-0eef-4875-ac4f-eae4a5b16956",
                           "Right Hon. John N. Timer@Leader of the Opposition":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Hon.   J.-J. Blais@Acting President of the Privy Council":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Right Hon. John N. Timer@Vancouver Quadra":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Mr. David  Bjomson@Selkirk":"62ced82d-e217-476b-93bd-0d457e6742d3",
                           "Mr.   de Corneille@":"ef1388ad-345b-4646-895f-26d8923ecf1b",
                           "Mr.   Dirner@Vancouver Quadra":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Hon.   J.-J. Blais@for the Minister of Agriculture":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Mr.   Wm. Andres@Parliamentary Secretary to Minister of State (Multiculturalisin":"f5130852-726b-4537-b4b3-400e85bc27fd",
                           "Mr.   Chas. L. Caccia@Davenport":"328b9cb9-24ea-4602-abb8-ff33227c2f3f",
                           "Mr. Ken  Janies@Parliamentary Secretary to Minister of Labour":"9117937f-b7bc-4454-8914-ddeecf186989",
                           "Hon.   Chas. L. Caccia@Minister of the Environment":"328b9cb9-24ea-4602-abb8-ff33227c2f3f",
                           "Mr. Della  Noce@":"94b62454-efbb-4091-91dc-ef9e0d03042d",
                           "Mr. Garth  Ttorner@Halton-Peel":"8935b46b-8d54-41eb-b32b-07568b4005a1",
                           "Mr. Garth  Tlimer@Halton-Peel":"8935b46b-8d54-41eb-b32b-07568b4005a1",
                           "Hon.   J.-J. Blais@Minister of National Defence":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Mr.   Manion@":"4f144b8d-0f62-4502-b6eb-6bf2aa0faaad",
                           "Hon. David  Crorabie@Rosedale":"9822cf68-94be-4d0c-9a5c-ba57f408fe81",
                           "Mr.   J.W. Bud Bird@Fredericton":"27d54edd-ee41-4a52-8c15-ec7dbb61ebf9",
                           "Hon.   J.-J. Blais@Postmaster General":"ed86593a-bdfd-491f-a581-3e6dd2aa8155",
                           "Right Hon. John N. Tinner@Leader of the Opposition":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Hon.   Donald. S. Macdonald@Minister of Finance":"3182f9f8-dbee-4324-93f2-30c9df730339",
                           "Mr. Rod  Biaker@Parliamentary Secretary to Minister of Supply and Services":"8b173462-ff95-47f1-a93e-a813c66ddd7b",
                           "Mr.   Ibrner@Vancouver Quadra":"2d6cfb9d-1d91-419c-835b-2bc796126fab",
                           "Mr. Walter Van  de Walle@Pembina":"c07e4f86-a8d4-4d58-8692-23d19fc34e34",
                           "Mr. Lyle Dean  Mac@":"9c8ce4b0-87b5-4ab6-9645-c4e81555e158"
                           }

        correctedspeecheslist = []

        for problemname in list(correctiondict.keys()):
            #print(problemname)
            qs = basehansard.objects.filter(speakername=problemname)
            #print("Speeches to correct: %s" % len(qs))
            for speech in qs:
                # Replace 'unmatched' pid with proper pid
                speech.pid = correctiondict[problemname]
                
                # Fill empty fields from adjacent examples of this person during this day, if available
                try:
                    correction_qs = basehansard.objects.filter(speechdate=speech.speechdate).filter(pid=correctiondict[problemname])
                    #print("Speeches in correction range: %s" % len(correction_qs))

                    speech.opid = correction_qs[0].opid
                    speech.speakeroldname = problemname
                    speech.speakername = correction_qs[0].speakername
                    speech.speakerparty = correction_qs[0].speakerparty
                    speech.speakerriding = correction_qs[0].speakerriding
                    speech.speakerurl = correction_qs[0].speakerurl
                    speech.gender = correction_qs[0].gender
                    speech.province = correction_qs[0].province
                    speech.government = correction_qs[0].government
                    speech.housesittings = correction_qs[0].housesittings
                    speech.majority = correction_qs[0].majority
                    speech.offopp = correction_qs[0].offopp
                    speech.popvote = correction_qs[0].popvote
                    speech.seatpct = correction_qs[0].seatpct
                    speech.party_fk = correction_qs[0].party_fk
                    speech.minister = correction_qs[0].minister
                    speech.pmorleader = correction_qs[0].pmorleader
                    speech.houseleader = correction_qs[0].houseleader
                    speech.juniorminister = correction_qs[0].juniorminister
                    speech.whip = correction_qs[0].whip
                    speech.pollpct = correction_qs[0].pollpct

                    speech.save()
                    
                except:
                    speech.speakeroldname = problemname # save the original here for safety reasons
                    
                    try:
                        const = constituency.objects.filter(pid=speech.pid, startdate__lte=speech.speechdate, enddate__gte=speech.speechdate).order_by('enddate')[0]
                        const_qs = basehansard.objects.filter(speechdate__lte=const.enddate, speechdate__gte=const.startdate, pid=speech.pid)

                        speech.opid = const_qs[0].opid
                        speech.speakeroldname = problemname
                        speech.speakername = const_qs[0].speakername
                        speech.speakerparty = const_qs[0].speakerparty
                        speech.speakerriding = const_qs[0].speakerriding
                        speech.speakerurl = const_qs[0].speakerurl
                        speech.gender = const_qs[0].gender
                        speech.province = const_qs[0].province
                        speech.government = const_qs[0].government
                        speech.housesittings = const_qs[0].housesittings
                        speech.majority = const_qs[0].majority
                        speech.offopp = const_qs[0].offopp
                        speech.popvote = const_qs[0].popvote
                        speech.seatpct = const_qs[0].seatpct
                        speech.party_fk = const_qs[0].party_fk

                        lead = "Prime Minister"
                        opplead = "Leader of the Official Opposition"
                        junior_minister_list = ["Secretary to the", "Secretary for", "Assistant to the", "Parliamentary Secretary"]
                        minister_list = ["Minister", "Solicitor General", "Secretary of State", "Postmaster General", "Superintendent-General"]
                        wh = "Whip"
                        hl = "House Leader"
                        h2 = "Leader of the Government"

                        poslist = position.objects.filter(pid__pid=speech.pid).filter(startdate__lte=speech.speechdate).filter(enddate__gte=speech.speechdate).values_list('positionname', flat=True)
                
                        if len(poslist)==0:
                            speech.pmorleader = False
                            speech.minister = False
                        else:
                            for aposition in poslist:
                                for jm in junior_minister_list:
                                    if jm in aposition:
                                        speech.juniorminister = True
                                if lead in aposition:
                                    if "Deputy" in aposition:
                                        speech.pmorleader = False
                                    elif "Secretary" in aposition:
                                        speech.pmorleader = False
                                        speech.minister = False
                                        speech.juniorminister = True
                                    else:
                                        speech.pmorleader = True
                                        speech.minister = True
                                elif opplead in aposition:
                                    if "Deputy" in aposition:
                                        speech.pmorleader = False
                                    else:
                                        speech.pmorleader = True
                                elif wh in aposition:
                                    speech.whip = True
                                elif hl in aposition:
                                    speech.houseleader=True
                                elif h2 in aposition:
                                    speech.houseleader=True
                                else:
                                    for m in minister_list:
                                        if aposition.startswith(m): # we assume that "true" ministers will have a title that begins with eg. "Minister"
                                            speech.minister = True

                        # Correct polling data

                        current_year = speech.speechdate.year
                        current_quarter = 0
                        month_int = speech.speechdate.month
                        if month_int <= 3:
                            current_quarter = 1
                        elif month_int <= 6:
                            current_quarter = 2
                        elif month_int <= 9:
                            current_quarter = 3
                        else:
                            current_quarter = 4

                        poll_qs = polls.objects.filter(party_fk=speech.party_fk).filter(year=current_year).filter(quarter=current_quarter)
                        if len(poll_qs)==0:
                            pass
                        else:
                            speech.pollpct = poll_qs.first().q_avg_pollpct
                            
                    except Exception, e:
                        print >> sys.stderr, "Exception: %s " % e
                        print >> sys.stderr, "Name: %s " % problemname
                        print >> sys.stderr, "PID: %s " % correctiondict[problemname]
                        print >> sys.stderr, "Date: %s" % speech.speechdate
                        
                        # sys.exit(1)

                speech.save()
                correctedspeecheslist.append(speech.basepk)

        print(correctedspeecheslist)
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
                           
  
   
