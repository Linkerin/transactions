"""
Accouting transactions fraud analysis application
Copyright (C) 2021  Alexey Gusev
GNU Affero General Public License v3.0
License: https://github.com/Linkerin/transactions/blob/main/license.txt
"""

import pandas as pd
import numpy as np
import concurrent.futures as ccf


class Transactions:

    def __init__(self):
        self.trans_columns = (
            'Дата',
            'Номер',
            'Назначение платежа',
            'Получатель',
            'Получатель.ИНН',
            'Счет получателя',
            'Вид операции',
            'Вх. номер',
            'Вх. дата',
            'Организация',
            'Банковский счет',
            'ЦФО',
            'Статья ДДС',
            'Договор.Номер договора',
            'Договор.Основная статья движения денежных средств',
            'Договор.Предмет договора',
            'Договор.Дата подписания',
            'Договор.Срок действия до',
            'Договор.Контрагент.ИНН',
            'Договор.Контрагент.Банковский счет',
            'Договор.ЦФО',
            'Договор.Условие по сроку договора',
            'Сумма'
        )

        self.contracts_columns = (
            'Договор контрагента',
            'ЦФО',
            'Статья движения денежных средств',
            'Аналитика 1',
            'Аналитика 2',
            'Аналитика 3',
            'Основное ЦФО / Статья ДДС',
            'Договор контрагента.Вид договора',
            'Договор контрагента.Номер договора',
            'Договор контрагента.Дата',
            'Договор контрагента.Срок действия до',
            'Договор контрагента.Планируется пролонгация',
            'Договор контрагента.Условие по сроку договора',
            'Договор контрагента.Контрагент',
            'Договор контрагента.Состояние',
            'Договор контрагента.Состояние судебного дела',
            'Договор контрагента.Валюта',
            'Договор контрагента.Организация'
        )

    def full_analysis(self, dataframes):
        """
        This method starts the analysis itself.\n
        `dataframes` parameter  is a dictionary with
        2 datasets inside:\n
        `{'data': transactions_dataset, 
        'contracts': contracts_dataset}`.\n
        Successful result of an `upload()` method returns 
        the dictionary in this format.
        """
        try:
            result = pd.concat([
                self.contract_validity(dataframes['data']),
                self.accounting_article(dataframes['data'], dataframes['contracts']),
                self.counterparty_inn(dataframes['data']),
                self.cfo(dataframes['data'], dataframes['contracts']),
                self.contracts_check(dataframes['data']),
                self.counterparty_account(dataframes['data']),
                self.duplicates(dataframes['data'])
                ]).sort_index()

            columns = list(result.columns.values)
            result = result[[columns[-1]] + columns[0:len(columns) - 1]]
        except TypeError as type_err:
            print(type_err)
            return f"Invalid file: тип данных не соответствует шаблону"
        except KeyError as key_err:
            print(key_err)
            return f"Invalid file: ошибка ключа словаря"


        return result

    def upload(self, data_src, contracts_src):
        with ccf.ProcessPoolExecutor() as executor:
            proc_1 = executor.submit(pd.read_excel, data_src)
            proc_2 = executor.submit(pd.read_excel, contracts_src)

            df_1 = proc_1.result()
            df_2 = proc_2.result()

        try:
            self.empty_columns_del([df_1, df_2])
            
            output = {}

            df_1_type = self.df_check(df_1)
            df_2_type = self.df_check(df_2)
            if df_1_type == 'transactions' and df_2_type == 'contracts':
                output['data'] = df_1
                output['contracts'] = df_2
            elif df_1_type == 'contracts' and df_2_type == 'transactions':
                output['data'] = df_2
                output['contracts'] = df_1
            else:
                if not df_1_type:
                    return f"Invalid file: {data_src.split('/')[-1]}"
                elif not df_2_type:
                    return f"Invalid file: {contracts_src.split('/')[-1]}"

            output['data'].set_index('Номер', inplace=True)
            total_filt = output['data']['Дата'] == 'Итого'
            output['data'].drop(index=output['data'][total_filt].index, inplace=True)

            #Correct conversion of float datatype to string via Int64 preserving NaN values
            output['data']['Получатель.ИНН'] = np.where(pd.isnull(output['data']['Получатель.ИНН']), 
                                                        output['data']['Получатель.ИНН'],
                                                        output['data']['Получатель.ИНН'].astype('Int64').astype(str))
            output['data']['Договор.Контрагент.ИНН'] = np.where(pd.isnull(output['data']['Договор.Контрагент.ИНН']), 
                                                        output['data']['Договор.Контрагент.ИНН'],
                                                        output['data']['Договор.Контрагент.ИНН'].astype('Int64').astype(str))

            output['data']['Договор.Дата подписания'] = pd.to_datetime(output['data']['Договор.Дата подписания'],
                                                                    format='%d.%m.%Y', errors='coerce')
            output['data']['Договор.Срок действия до'] = pd.to_datetime(output['data']['Договор.Срок действия до'],
                                                                        format='%d.%m.%Y', errors='coerce')
            output['data']['Дата'] = pd.to_datetime(output['data']['Дата'],
                                                    format='%d.%m.%Y %H:%M:%S', errors='coerce')
            output['data']['Вх. дата'] = pd.to_datetime(output['data']['Вх. дата'],
                                                        format='%d.%m.%Y', errors='coerce')
        except KeyError as err:
            print(err)
            return f"Invalid file: ошибка ключа словаря"

        return output

    # 
    def df_check(self, df):
        """ This method checks data validity
            and identifies which file contains
            transactions and which one - contracts.
        """
        trans_col_check = list(map(lambda x: True if x in self.trans_columns else False, df.columns))
        contracts_col_check = list(map(lambda x: True if x in self.contracts_columns else False, \
                                df.columns))

        if set(trans_col_check) == {True} and len(trans_col_check) == 23:
            return 'transactions'
        elif set(contracts_col_check) == {True} and len(contracts_col_check) >= 15:
            return 'contracts'

        return False

    def empty_columns_del(self, dataframe):
        for _, data in enumerate(dataframe): 
            columns_list = []
            for column in data.columns:
                if 'Unnamed:' in str(column):
                    columns_list.append(column)
            data.drop(columns=columns_list, inplace=True)
        return

    # All the methods regarding red flags implemented below

    def contract_validity(self, data):
        date_terms_exclusions = (
            'Возможность автопролонгации',
            'Бессрочно / До расторжения / На неопределенный срок',
            'До полного исполнения обязательств'
        )
        contract_num_exlusions = (
            'б/н',
            'По заявке',
            'По счетам',
            'по счетам',
            'Постановление №1170',
            'Порядок выплаты',
            'Счет по определению',
            'Счет по определению2',
            'нет номера'
        )

        contract_validity_check = (data['Договор.Условие по сроку договора'].apply(lambda x: x not in date_terms_exclusions)) & \
                                (data['Договор.Номер договора'].apply(lambda x: x not in contract_num_exlusions)) & \
                                (data['Статья ДДС'] != 'Движение денежных средств по закладным') & \
                                (data['Дата'].dt.date > data['Договор.Срок действия до'])
        contract_validity_alerts = pd.DataFrame(data[contract_validity_check])
        contract_validity_alerts['Alert_type'] = 'Проверка срока действия договора'

        return contract_validity_alerts


    def accounting_article (self, data, contracts_info):
        contract_num_exlusions = (
            'По заявке',
            'б/н',
            'По счетам',
            'по счетам'
        )

        accounting_article_filt = ((data['Статья ДДС'] == 'Группа. Перечисление  ОД + % и пр. по закладным инвестора') & \
                                (data['Получатель.ИНН'] == '7727290538') == False) & \
                                ((data['Статья ДДС'] == 'Движение денежных средств по закладным') & \
                                (data['Договор.Основная статья движения денежных средств'] == 'Рефинансирование (выкуп) закладных') == False) & \
                                ((data['Статья ДДС'] == 'Движение денежных средств по закладным') & \
                                (data['Договор.Основная статья движения денежных средств'] == 'Продажа закладных поставщикам, ОД + %') == False) & \
                                ((data['Статья ДДС'] == 'Гос.пошлина (иски, прочее)') & \
                                (data['Договор.Основная статья движения денежных средств'] == 'Судебные расходы') == False) & \
                                ((data['Статья ДДС'] == 'АД: Госпошлина и другие обязательные платежи в бюджет') & \
                                (data['Договор.Основная статья движения денежных средств'] == 'Судебные расходы') == False)
        accounting_article_check = (data['Договор.Номер договора'].apply(lambda x: x not in contract_num_exlusions)) & \
                                (data['Договор.Номер договора'].notnull()) & \
                                (data['Статья ДДС'] != data['Договор.Основная статья движения денежных средств'])
        accounting_article_alerts = pd.DataFrame(data[accounting_article_filt & accounting_article_check])

        accounting_article_alerts['Temp_key'] = accounting_article_alerts['Договор.Номер договора'].apply(str) + \
                                                accounting_article_alerts['Статья ДДС'].apply(str)
        contracts_info['Temp_key'] = contracts_info['Договор контрагента.Номер договора'].apply(str) + \
                                    contracts_info['Статья движения денежных средств'].apply(str)
        contracts_filt = accounting_article_alerts['Temp_key'].apply(lambda x: x not in contracts_info['Temp_key'].values)

        accounting_article_alerts = accounting_article_alerts[contracts_filt]
        accounting_article_alerts['Alert_type'] = 'Проверка статьи ДДС'
        accounting_article_alerts.drop(columns='Temp_key', inplace=True)
        contracts_info.drop(columns='Temp_key', inplace=True)

        return accounting_article_alerts


    def counterparty_inn(self, data):
        counterparty_inn_exclusions = data['Договор.Контрагент.ИНН'].notnull()
        counterparty_inn_check = data['Получатель.ИНН'] != data['Договор.Контрагент.ИНН']
        counterparty_inn_alerts = pd.DataFrame(data[counterparty_inn_exclusions & counterparty_inn_check])
        counterparty_inn_alerts['Alert_type'] = 'Проверка соответствия ИНН'

        return counterparty_inn_alerts


    def cfo(self, data, contracts_info):
        cfo_check = (data['Договор.Номер договора'] != 'По заявке') & \
                    (data['Договор.Номер договора'] != 'б/н') & (data['Договор.Номер договора'].notnull()) & \
                    (data['ЦФО'].notnull()) & (data['ЦФО'] != data['Договор.ЦФО'])

        cfo_alerts = pd.DataFrame(data[cfo_check])
        cfo_alerts['Temp_key'] = cfo_alerts['Договор.Номер договора'].apply(str) + cfo_alerts['ЦФО'].apply(str)
        contracts_info['Temp_key'] = contracts_info['Договор контрагента.Номер договора'].apply(str) + \
                                    contracts_info['ЦФО'].apply(str)
        contracts_filt = cfo_alerts['Temp_key'].apply(lambda x: x not in contracts_info['Temp_key'].values)

        cfo_alerts = cfo_alerts[contracts_filt]
        cfo_alerts['Alert_type'] = 'Проверка соответствия ЦФО'
        cfo_alerts.drop(columns='Temp_key', inplace=True)
        contracts_info.drop(columns='Temp_key', inplace=True)

        return cfo_alerts


    def contracts_check(self, data):
        aa_exclusions = (
            'Движение средств по номинальному счету застройщика',
            'Выплата компенсаций дольщикам', 'Оплата труда',
            'Перечисление ДС на ведение хозяйственной деятельности внутри организации',
            'Квартальная премия',
            'Движение денежных средств по закладным',
            'Недвижимость: Коммунальные услуги и прочие расходы по недвижимости',
            'Недвижимость: Гос.пошлина при постановке на баланс',
            'Отклонения курса продажи (покупки) иностранной валюты от официального курса',
            'Гос.пошлина (иски, прочее)',
            'Индивидуальные занятия спортом',
            'Комиссия банка за расчетно-кассовое обслуживание',
            'Группа. Комиссия банка за расчетно-кассовое обслуживание',
            'Реферальная программа',
            'АД: Судебные расходы',
            'Судебные расходы',
            'Годовой бонус (премия)',
            'Мотивация',
            'Командировочные расходы',
            'Вознаграждение членам Правления',
            'Вознаграждение членов НС за участие в работе НС и в работе комитетов НС',
            'Вознаграждение членов комитетов НС за участие в работе комитетов НС',
            'Вознаграждение членам ревизионной комиссии',
            'Группа. Выкуп закладных, ОД + %'
        )
        trans_type_exclusions = ['Уплата налога', 'Перевод на другой счет организации', 'Перечисление подотчетному лицу']
        recipient_exclusions = ['7707780887', '7710168360', '6731010703', '6731048270'] #Минстрой, Минфин, УФК и УФССП по Смоленской области

        contracts_check = (data['Статья ДДС'].apply(lambda x: x not in aa_exclusions)) & \
                        (data['Статья ДДС'].apply(lambda x: x[0:6] != 'Налоги')) & \
                        (data['Вид операции'].apply(lambda x: x not in trans_type_exclusions)) & \
                        (data['Получатель.ИНН'].apply(lambda x: x not in recipient_exclusions)) & \
                        (data['Договор.Номер договора'].isna())
        contracts_alerts = pd.DataFrame(data[contracts_check])
        contracts_alerts['Alert_type'] = 'Проверка на наличие договора в платеже'

        return contracts_alerts


    def counterparty_account(self, data):
        aa_exclusions = (
            'Группа. Выкуп закладных, ОД + %',
            'Движение денежных средств по закладным',
            'Перечисление ДС на брокерские счета',
            'Программа льготного ипотечного кредитования 6,5%',
            'Программа льготного кредитования застройщиков',
            'О: Выплата купона',
            'Комиссия за кредитный риск',
            'Комиссии за услуги сервисных агентов',
            'Комиссии за услуги сервисных агентов (Портфель инвесторов)',
            'Комиссия за депозитарное хранение и учет закладных',
            'Комиссия банка за расчетно-кассовое обслуживание',
            'Комиссия платежному агенту',
            'Комиссия биржи: сборы',
            'Депозит. Размещение средств в депозиты',
            'Группа. Перечисление  ОД + % и пр. по закладным инвестора',
            'Информационные услуги по ЦБ'
        )
        contracts_exclusions = (
            'По счетам',
            'по счетам',
            'Подтверждение',
            'Постановление №1609',
            'Постановление № 1609',
            'Постановление №1170'
        )
        recipient_exclusions = (
            '7704366195', #ДОМ.РФ Управление активами
            '7702165310', #НКО АО НРД
            '7725038124', #Банк ДОМ.РФ
            '7727290538', #ДОМ.РФ Ипотечный агент
            '7729355614'  #АО ДОМ.РФ
        )

        counterparty_account_check = (data['Статья ДДС'].apply(lambda x: x not in aa_exclusions)) & \
                                    (data['Договор.Номер договора'].apply(lambda x: x not in contracts_exclusions)) & \
                                    (data['Договор.Номер договора'].notnull()) & \
                                    (data['Счет получателя'].notnull()) & \
                                    (data['Договор.Контрагент.Банковский счет'].notnull()) & \
                                    (data['Получатель'].str.contains('банк', case=False, na=False) == False) & \
                                    (data['Получатель.ИНН'].apply(lambda x: x not in recipient_exclusions)) & \
                                    (data['Счет получателя'] != data['Договор.Контрагент.Банковский счет'])
        counterparty_account_alerts = pd.DataFrame(data[counterparty_account_check])
        counterparty_account_alerts['Alert_type'] = 'Проверка номера счета контрагента'

        return counterparty_account_alerts


    def duplicates(self, data):
        aa_exclusions = (
            'Комиссия банка за расчетно-кассовое обслуживание',
            'Группа. Комиссия банка за расчетно-кассовое обслуживание',
            'Гос.пошлина (иски, прочее)',
            'Налоги. НДС',
            'Налоги. Налог на имущество',
            'Налоги. Земельный налог',
            'Комиссия биржи: сборы',
            'ЦБ: Комиссия за депозитарные услуги',
            'АЖ: Госпошлина при регистрации недвижимости',
            'УН: Гос пошлина, судебные, и аналогичные расходы'
        )

        duplicate_filt = (
            (
                (data['Статья ДДС'] == 'Перечисление ДС на брокерские счета')
                & (data['Получатель.ИНН'] == '7750004023') == False
            )
            & (
                (data['Статья ДДС'] == 'Перечисление ДС на ведение хозяйственной деятельности внутри организации')
                & (data['Получатель.ИНН'] == '7729355614') == False
            )
            & (data['Статья ДДС'].apply(lambda x: x not in aa_exclusions))
            & (
                (data['Статья ДДС'] == 'О: Расходы по выпуску ИЦБ')
                & (data['ЦФО'] == 'ИА_Секьюритизация и эмиссия облигаций')
                & (data['Получатель.ИНН'] == '7702077840') == False
            )
            & ((data['Получатель'] == data['Организация']) == False)
        )

        dupl_check_1 = data[duplicate_filt].duplicated(subset=['Дата', 'Сумма', 'Получатель.ИНН', 'Счет получателя', 'Назначение платежа'], keep=False)
        dupl_check_2 = data[duplicate_filt].duplicated(subset=['Дата', 'Сумма', 'Получатель.ИНН', 'Назначение платежа'], keep=False)
        dupl_check_3 = data[duplicate_filt].duplicated(subset=['Дата', 'Сумма', 'Счет получателя', 'Назначение платежа'], keep=False)

        duplicated_transactions_1 = pd.DataFrame(data[duplicate_filt][dupl_check_1])
        duplicated_transactions_2 = pd.DataFrame(data[duplicate_filt][dupl_check_2])
        duplicated_transactions_3 = pd.DataFrame(data[duplicate_filt][dupl_check_3])

        duplicated_transactions_alerts = pd.merge(duplicated_transactions_1.reset_index(), \
                                        duplicated_transactions_2.reset_index(), how='outer')
        duplicated_transactions_alerts = pd.merge(duplicated_transactions_alerts, \
                                        duplicated_transactions_3.reset_index(), how='outer').set_index('Номер')
        duplicated_transactions_alerts['Alert_type'] = 'Проверка на дубликаты'

        return duplicated_transactions_alerts
