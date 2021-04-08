# Accouting transactions analysis tool
![Upload screen](./upload_screen.png "Application upload screen")

## About
This is a tool based on [Flask framework](https://flask.palletsprojects.com/en/1.1.x/) made for internal corporate needs. As an input it takes Excel files with accounting transactions for the period and all the company's contracts. Using Pandas library it analyses accouting transactions according to several rules and creates alerts if something suspicious is found.

## Input requirements
The application proceeds two Excel (*.xls, *.xlsx) files: one containing accouting transactions and the other one - company's contracts.

#### Accounting transactions fields:
| Field                    | Type                          | Required |
| ------------------------ |-------------------------------| :-------:|
| Дата                     | Datetime, DD.MM.YYYY HH:MM:SS | Yes      |
| Номер                    | String                        | Yes      |
| Назначение платежа       | String                        | Yes      |
| Получатель               | String                        | No       |
| Получатель.ИНН           | Number                        | No       |
| Счет получателя          | String                        | No       |
| Вид операции             | String                        | Yes      |
| Вх. номер                | String                        | No       |
| Вх. дата                 | Date, DD.MM.YYYY              | No       |
| Организация              | String                        | No       |
| Банковский счет          | String                        | No       |
| ЦФО                      | String                        | No       |
| Статья ДДС               | String                        | No       |
| Договор.Номер договора   | String                        | No       |
| Договор.Основная статья движения денежных средств | String | No     |
| Договор.Предмет договора | String                        | No       |
| Договор.Дата подписания  | Date, DD.MM.YYYY              | No       |
| Договор.Срок действия до | Date, DD.MM.YYYY              | No       |
| Договор.Контрагент.ИНН   | Number                        | No       |
| Договор.Контрагент.Банковский счет | String              | No       |
| Договор.Контрагент.ЦФО   | String                        | No       |
| Договор.Условие по сроку договора | String               | No       |
| Сумма                    | Number                        | No       |

#### Contracts fields:
| Field                     | Type                          | Required |
| ------------------------- |-------------------------------| :-------:|
| Договор контрагента       | String                        | Yes      |
| ЦФО                       | String                        | Yes      |
| Статья движения денежных средств | String                 | Yes      |
| Основное ЦФО / Статья ДДС | Boolen                        | Yes      |
| Договор контрагента.Вид договора   | String               | No       |
| Договор контрагента.Номер договора | String               | No       |
| Договор контрагента.Дата  | Date, DD.MM.YYYY              | No       |
| Договор контрагента.Срок действия до | Date, DD.MM.YYYY   | No       |
| Договор контрагента.Планируется пролонгация   | Boolen    | No       |
| Договор контрагента.Условие по сроку договора | String    | No       |
| Договор контрагента.Контрагент | String                   | No       |
| Договор контрагента.Состояние  | String                   | No       |
| Договор контрагента.Состояние судебного дела | String     | No       |
| Договор контрагента.Валюта      | String                  | No       |
| Договор контрагента.Организация | String                  | No       |

## Output
Excel file with analysis results. The format is the same as for accounting transactions file with an additional field:

| Field      | Type   |
| ---------- |--------|
| Alert type | String |

List of alert types:
* Проверка срока действия договора
* Проверка статьи ДДС
* Проверка соответствия ИНН
* Проверка соответствия ЦФО
* Проверка на наличие договора в платеже
* Проверка номера счета контрагента
* Проверка на дубликаты