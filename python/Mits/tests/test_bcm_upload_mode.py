from Mits.Families.Samsung.BcmUploadModeConsts import MODELS 
c = ClientBcmUploadMode()
try :
    c.dump(MODELS.S8XXX)
    c.restore_debug_level_and_finalize()
except :