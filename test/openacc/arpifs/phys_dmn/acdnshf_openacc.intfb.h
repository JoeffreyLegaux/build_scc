INTERFACE
  SUBROUTINE ACDNSHF_OPENACC (YDCST, YDPHY, YDPHY1, KIDIA, KFDIA, KLON, KTDIA, KLEV, PEMIS, PLSM, PNEIJ, PQ, PQS, PTS, PCHROV,  &
  & PDQSTS, PDERNSHF, YDSTACK)
!$acc routine( ACDNSHF_OPENACC ) seq
    
    USE PARKIND1, ONLY: JPIM, JPRB
    USE YOMHOOK, ONLY: LHOOK, DR_HOOK, JPHOOK
    
    USE YOMPHY, ONLY: TPHY
    USE YOMCST, ONLY: TCST
    USE YOMPHY1, ONLY: TPHY1
    
    !     ------------------------------------------------------------------
    
    USE STACK_MOD
    
    IMPLICIT NONE
    
    TYPE(TCST), INTENT(IN) :: YDCST
    TYPE(TPHY), INTENT(IN) :: YDPHY
    TYPE(TPHY1), INTENT(IN) :: YDPHY1
    INTEGER(KIND=JPIM), INTENT(IN) :: KLON
    INTEGER(KIND=JPIM), INTENT(IN) :: KLEV
    INTEGER(KIND=JPIM), INTENT(IN) :: KIDIA
    INTEGER(KIND=JPIM), INTENT(IN) :: KFDIA
    INTEGER(KIND=JPIM), INTENT(IN) :: KTDIA
    REAL(KIND=JPRB), INTENT(IN) :: PEMIS(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PLSM(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PNEIJ(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PQ(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PQS(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PTS(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PCHROV(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PDQSTS(KLON)
    REAL(KIND=JPRB), INTENT(OUT) :: PDERNSHF(KLON)
    
    !     ------------------------------------------------------------------
    
    
    
    
    !     ------------------------------------------------------------------
    
    TYPE(STACK), INTENT(IN) :: YDSTACK
  END SUBROUTINE ACDNSHF_OPENACC
END INTERFACE
