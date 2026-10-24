
# email templates
class EmailTemplates:
    def OTPEmailTemplate(username:str, otp:int):
        return f"""Hello {username},
        Thanks for registering to SNS Management App
        your OTP:{otp}
        
        If you did't registered for this app ignore this email and
        don't OTP with any one.

        Regards
        SNS Management App
        """

    @staticmethod
    def ResetPasswordTemplate(link:str,username:str="User"):
        template = f"""Dear {username},
        Thanks for using SNS Management App to manage your notes and files,
        Password Reset Link : {link}
        If your not doing this simply, ignore this email.

        Regards
        SNS Management App
        """
        return template