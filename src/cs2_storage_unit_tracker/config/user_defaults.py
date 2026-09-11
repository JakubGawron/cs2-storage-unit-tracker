from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True, slots=True, kw_only=True)
class SteamApiSettings:
    # Steam game app ID to track prices for.
    # Find app ID at: https://steamdb.info/
    # Default Counter-Strike 2 (app ID: 730)
    app_id: int = 730

    # Currency used by Steam api when retrieving prices (iso code).
    currency: str = "USD"


@dataclass(frozen=True, slots=True, kw_only=True)
class FrankfurterApiSettings:
    # Currency to convert prices into (iso code).
    to_currency: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class FormattingSettings:
    source_currency_use_locale: bool = True
    exchanged_currency_use_locale: bool = True

    fallback_format: str = "#,##0.00 ¤¤"

    currency_locales: MappingProxyType[str, str] = MappingProxyType(
        {
            "AED": "ar_AE",
            "AFN": "fa_AF",
            "ALL": "sq_AL",
            "AMD": "hy_AM",
            "ANG": "nl_CW",
            "AOA": "pt_AO",
            "ARS": "es_AR",
            "AUD": "en_AU",
            "AWG": "nl_AW",
            "AZN": "az_AZ",
            "BAM": "bs_BA",
            "BBD": "en_BB",
            "BDT": "bn_BD",
            "BHD": "ar_BH",
            "BIF": "fr_BI",
            "BMD": "en_BM",
            "BND": "ms_BN",
            "BOB": "es_BO",
            "BRL": "pt_BR",
            "BSD": "en_BS",
            "BTN": "dz_BT",
            "BWP": "en_BW",
            "BYN": "be_BY",
            "BZD": "en_BZ",
            "CAD": "en_CA",
            "CDF": "fr_CD",
            "CHF": "de_CH",
            "CLP": "es_CL",
            "CNH": "zh_CN",
            "CNY": "zh_CN",
            "COP": "es_CO",
            "CRC": "es_CR",
            "CUP": "es_CU",
            "CVE": "pt_CV",
            "CZK": "cs_CZ",
            "DJF": "fr_DJ",
            "DKK": "da_DK",
            "DOP": "es_DO",
            "DZD": "ar_DZ",
            "EGP": "ar_EG",
            "ERN": "ti_ER",
            "ETB": "am_ET",
            "EUR": "de_DE",
            "FJD": "en_FJ",
            "FKP": "en_FK",
            "GBP": "en_GB",
            "GEL": "ka_GE",
            "GGP": "en_GG",
            "GHS": "en_GH",
            "GIP": "en_GI",
            "GMD": "en_GM",
            "GNF": "fr_GN",
            "GTQ": "es_GT",
            "GYD": "en_GY",
            "HKD": "zh_HK",
            "HNL": "es_HN",
            "HTG": "fr_HT",
            "HUF": "hu_HU",
            "IDR": "id_ID",
            "ILS": "he_IL",
            "IMP": "en_IM",
            "INR": "en_IN",
            "IQD": "ar_IQ",
            "IRR": "fa_IR",
            "ISK": "is_IS",
            "JEP": "en_JE",
            "JMD": "en_JM",
            "JOD": "ar_JO",
            "JPY": "ja_JP",
            "KES": "en_KE",
            "KGS": "ky_KG",
            "KHR": "km_KH",
            "KMF": "fr_KM",
            "KPW": "ko_KP",
            "KRW": "ko_KR",
            "KWD": "ar_KW",
            "KYD": "en_KY",
            "KZT": "kk_KZ",
            "LAK": "lo_LA",
            "LBP": "ar_LB",
            "LKR": "si_LK",
            "LRD": "en_LR",
            "LSL": "en_LS",
            "LYD": "ar_LY",
            "MAD": "ar_MA",
            "MDL": "ro_MD",
            "MGA": "mg_MG",
            "MKD": "mk_MK",
            "MMK": "my_MM",
            "MNT": "mn_MN",
            "MOP": "zh_MO",
            "MRO": "fr_MR",
            "MRU": "ar_MR",
            "MUR": "en_MU",
            "MVR": "dv_MV",
            "MWK": "en_MW",
            "MXN": "es_MX",
            "MYR": "ms_MY",
            "MZN": "pt_MZ",
            "NAD": "en_NA",
            "NGN": "en_NG",
            "NIO": "es_NI",
            "NOK": "nb_NO",
            "NPR": "ne_NP",
            "NZD": "en_NZ",
            "OMR": "ar_OM",
            "PAB": "es_PA",
            "PEN": "es_PE",
            "PGK": "en_PG",
            "PHP": "en_PH",
            "PKR": "ur_PK",
            "PLN": "pl_PL",
            "PYG": "es_PY",
            "QAR": "ar_QA",
            "RON": "ro_RO",
            "RSD": "sr_RS",
            "RWF": "rw_RW",
            "SAR": "ar_SA",
            "SBD": "en_SB",
            "SCR": "en_SC",
            "SDG": "ar_SD",
            "SEK": "sv_SE",
            "SGD": "en_SG",
            "SHP": "en_SH",
            "SLE": "en_SL",
            "SOS": "so_SO",
            "SRD": "nl_SR",
            "SSP": "en_SS",
            "STN": "pt_ST",
            "SVC": "es_SV",
            "SYP": "ar_SY",
            "SZL": "en_SZ",
            "THB": "th_TH",
            "TJS": "tg_TJ",
            "TMT": "tk_TM",
            "TND": "ar_TN",
            "TOP": "to_TO",
            "TRY": "tr_TR",
            "TTD": "en_TT",
            "TWD": "zh_TW",
            "TZS": "sw_TZ",
            "UAH": "uk_UA",
            "UGX": "en_UG",
            "USD": "en_US",
            "UYU": "es_UY",
            "UZS": "uz_UZ",
            "VES": "es_VE",
            "VND": "vi_VN",
            "VUV": "en_VU",
            "WST": "en_WS",
            "XAF": "fr_CM",
            "XAG": "en_US",
            "XAU": "en_US",
            "XCD": "en_AG",
            "XCG": "nl_CW",
            "XDR": "en_US",
            "XOF": "fr_SN",
            "XPD": "en_US",
            "XPF": "fr_PF",
            "XPT": "en_US",
            "YER": "ar_YE",
            "ZAR": "en_ZA",
            "ZMW": "en_ZM",
            "ZWG": "en_ZW",
        }
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class GeneralSettings:
    reset_after_hours: int = 24


@dataclass(frozen=True, slots=True, kw_only=True)
class UserDefaults:
    steam_api = SteamApiSettings()
    frankfurter_api = FrankfurterApiSettings()
    formatting = FormattingSettings()
    general = GeneralSettings()


USER_DEFAULTS = UserDefaults()
