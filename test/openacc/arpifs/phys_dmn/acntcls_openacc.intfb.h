INTERFACE
  SUBROUTINE ACNTCLS_OPENACC (YDPHY, YDPHY0, YDCST, KIDIA, KFDIA, KLON, KLEV, PAPRS, PAPRSF, PCP, PQ, PT, PU, PV, PCD, PCDN,  &
  & PCDMR, PCDNMR, PCDNH, PCH, PCPS, PDPHI, PDPHIT, PDPHIV, PQS, PSTAB, PTS, PQCLS, PRHCLS, PTCLS, PUCLS, PVCLS, PUCLN, PVCLN,  &
  & PZPCLS, YDSTACK)
!$acc routine( ACNTCLS_OPENACC ) seq
    
    USE PARKIND1, ONLY: JPIM, JPRB
    USE YOMHOOK, ONLY: LHOOK, DR_HOOK, JPHOOK
    
    USE YOMPHY, ONLY: TPHY
    USE YOMCST, ONLY: TCST
    USE YOMPHY0, ONLY: TPHY0
    
    !-----------------------------------------------------------------------
    
    USE STACK_MOD
    
    IMPLICIT NONE
    
    INTEGER(KIND=JPIM), INTENT(IN) :: KLON
    INTEGER(KIND=JPIM), INTENT(IN) :: KLEV
    
    TYPE(TPHY), INTENT(IN) :: YDPHY
    TYPE(TPHY0), INTENT(IN) :: YDPHY0
    TYPE(TCST), INTENT(IN) :: YDCST
    INTEGER(KIND=JPIM), INTENT(IN) :: KIDIA
    INTEGER(KIND=JPIM), INTENT(IN) :: KFDIA
    REAL(KIND=JPRB), INTENT(IN) :: PAPRS(KLON, 0:KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PAPRSF(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PCP(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PQ(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PT(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PU(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PV(KLON, KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PCD(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PCDN(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PCDMR(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PCDNMR(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PCDNH(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PCH(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PCPS(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PDPHI(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PDPHIT(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PDPHIV(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PQS(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PSTAB(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PTS(KLON)
    REAL(KIND=JPRB), INTENT(OUT) :: PQCLS(KLON)
    REAL(KIND=JPRB), INTENT(OUT) :: PRHCLS(KLON)
    REAL(KIND=JPRB), INTENT(OUT) :: PTCLS(KLON)
    REAL(KIND=JPRB), INTENT(OUT) :: PUCLS(KLON)
    REAL(KIND=JPRB), INTENT(OUT) :: PVCLS(KLON)
    REAL(KIND=JPRB), INTENT(OUT) :: PUCLN(KLON)
    REAL(KIND=JPRB), INTENT(OUT) :: PVCLN(KLON)
    REAL(KIND=JPRB), INTENT(OUT) :: PZPCLS(KLON)
    
    !-----------------------------------------------------------------------
    
    
    
    !-----------------------------------------------------------------------
    
    TYPE(STACK), INTENT(IN) :: YDSTACK
  END SUBROUTINE ACNTCLS_OPENACC
END INTERFACE
