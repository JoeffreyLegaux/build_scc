INTERFACE
SUBROUTINE MF_PHYS_BAYRAD_OPENACC (YDCPG_BNDS, YDCPG_OPTS, PBAY_QRCONV&
&, PBAY_QSCONV, PRCONV_T1, PSCONV_T1, YDMODEL, YDSTACK)
!$acc routine (MF_PHYS_BAYRAD_OPENACC) seq
USE PARKIND1,ONLY:JPIM, JPRB
USE FIELD_VARIABLES_MOD,ONLY:FIELD_VARIABLES
USE TYPE_MODEL,ONLY:MODEL
USE CPG_OPTS_TYPE_MOD,ONLY:CPG_BNDS_TYPE, CPG_OPTS_TYPE
USE STACK_MOD
IMPLICIT NONE
TYPE (CPG_BNDS_TYPE), INTENT (IN)::YDCPG_BNDS
TYPE (CPG_OPTS_TYPE), INTENT (IN)::YDCPG_OPTS
REAL (KIND=JPRB), INTENT (IN)::PBAY_QRCONV (YDCPG_OPTS%KLON, 1:YDCPG_OPTS%KFLEVG)
REAL (KIND=JPRB), INTENT (IN)::PBAY_QSCONV (YDCPG_OPTS%KLON, 1:YDCPG_OPTS%KFLEVG)
REAL (KIND=JPRB), INTENT (OUT)::PRCONV_T1 (YDCPG_OPTS%KLON, YDCPG_OPTS%KFLEVG)
REAL (KIND=JPRB), INTENT (OUT)::PSCONV_T1 (YDCPG_OPTS%KLON, YDCPG_OPTS%KFLEVG)
TYPE (MODEL), INTENT (IN)::YDMODEL
TYPE(STACK) :: YDSTACK
ENDSUBROUTINE MF_PHYS_BAYRAD_OPENACC

END INTERFACE
