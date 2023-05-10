from pathlib import Path

import yaml

from Exceptions.InvalidCredentialException import InvalidCredentialsException


class Config:
    def __init__(self, configPath: str) -> None:
        """
        加载配置文件到Config类中定义的数据类型中
        :param configPath:
        """
        self.accounts = {}
        self.email = ""
        try:
            configPath = self.__findConfig(configPath)
            with open(configPath, 'r',encoding='utf-8') as f:
                config = yaml.safe_load(f)
                settings = config.get("settings")
                if settings["autofill_account"]:
                    number = settings["begin_num"]
                    for i in range(settings["account_nums"]):
                        self.accounts[i] = {
                            "username": settings["prefix_username"] + str(number),
                            "password": settings["common_password"]
                        }
                        number += 1
                else:
                    accs = config["accounts"]
                    for account in accs:
                        # 对于字典，循环的是key，即 account = 1,2
                        self.accounts[account] = {
                            "username": accs[account]["username"],
                            "password": accs[account]["password"]
                        }
                self.email = settings["email"]
                if not self.accounts or not self.email:
                    raise InvalidCredentialsException
        except FileNotFoundError as ex:
            print(
                f"[red]CRITICAL ERROR: The configuration file cannot be found at {configPath}")
            print("Press any key to exit...")
            input()
            raise ex
        except InvalidCredentialsException as ex:
            print(
                f"[red]CRITICAL ERROR: 在config.yaml中未添加需要创建的账号"
            )
            print("Press any key to exit...")
            input()
            raise ex
        except Exception as ex:
            print(
                f"[red]CRITICAL ERROR: 我也不知道是哪些错误"
            )
            input()
            raise ex



    def getAccount(self, account: str) -> dict:
        return self.accounts[account]


    def __findConfig(self,configPath):
        """
        查找配置文件是否在其他路径中,并将字符串路径转化为Path类型路径
        :param configPath:
        :return:
        """
        configPath = Path(configPath)
        if configPath.exists():
            return configPath
        if Path("settings/config.yaml").exists():
            return Path("settings/config.yaml")
        if Path("config/config.yaml").exists():
            return Path("config/config.yaml")
        return configPath


if __name__ == '__main__':
    a = Config('./settings/config.yaml')
    print(a.accounts)
    print(a.email)