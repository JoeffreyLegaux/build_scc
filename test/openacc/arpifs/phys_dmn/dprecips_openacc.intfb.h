INTERFACE
  SUBROUTINE DPRECIPS_OPENACC (YDCST, YDPRECIPS, KIDIA, KFDIA, KLON, KLEV, POROG, PCLSTPW, PDIAGH, PAPHIFM, PDZZ, PTPW, PQCM,  &
  & PFPLSL, PFPLSN, PFPLSG, PDPRECIPS, YDSTACK)
!$acc routine( DPRECIPS_OPENACC ) seq
    
    USE PARKIND1, ONLY: JPIM, JPRB
    USE YOMHOOK, ONLY: LHOOK, DR_HOOK, JPHOOK
    USE YOMDPRECIPS, ONLY: TDPRECIPS
    USE YOMCST, ONLY: TCST
    
    !     ------------------------------------------------------------------
    
    USE STACK_MOD
    
    IMPLICIT NONE
    
    TYPE(TCST), INTENT(IN) :: YDCST
    TYPE(TDPRECIPS), TARGET, INTENT(IN) :: YDPRECIPS
    
    !     ------------------------------------------------------------------
    
    INTEGER(KIND=JPIM), INTENT(IN) :: KIDIA
    INTEGER(KIND=JPIM), INTENT(IN) :: KFDIA
    INTEGER(KIND=JPIM), INTENT(IN) :: KLON
    INTEGER(KIND=JPIM), INTENT(IN) :: KLEV
    REAL(KIND=JPRB), INTENT(IN) :: POROG(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PCLSTPW(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PDIAGH(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PAPHIFM(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PDZZ(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PTPW(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PQCM(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PFPLSL(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PFPLSN(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PFPLSG(KLON)
    REAL(KIND=JPRB), INTENT(OUT) :: PDPRECIPS(KLON)
    
    
    
    TYPE(STACK), INTENT(IN) :: YDSTACK
  END SUBROUTINE DPRECIPS_OPENACC
END INTERFACE
