INTERFACE
  SUBROUTINE SUOZON_OPENACC (KIDIA, KFDIA, KLON, KLEV, PROFO3, LDQINT, PRESI, PRDELP, LD_LO3ABC, PVO3A, PVO3B, PVO3C, YDSTACK)
!$acc routine( SUOZON_OPENACC ) seq
    
    USE PARKIND1, ONLY: JPIM, JPRB
    USE YOMHOOK, ONLY: LHOOK, DR_HOOK, JPHOOK
    
    USE STACK_MOD
    
    IMPLICIT NONE
    
    INTEGER(KIND=JPIM), INTENT(IN) :: KLON
    INTEGER(KIND=JPIM), INTENT(IN) :: KLEV
    INTEGER(KIND=JPIM), INTENT(IN) :: KIDIA
    INTEGER(KIND=JPIM), INTENT(IN) :: KFDIA
    REAL(KIND=JPRB), INTENT(OUT) :: PROFO3(KLON, 0:KLEV)
    LOGICAL, INTENT(IN) :: LDQINT
    REAL(KIND=JPRB), INTENT(IN) :: PRESI(KLON, 0:KLEV)
    REAL(KIND=JPRB), INTENT(IN) :: PRDELP(KLON, KLEV)
    LOGICAL, INTENT(IN) :: LD_LO3ABC
    REAL(KIND=JPRB), INTENT(IN) :: PVO3A(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PVO3B(KLON)
    REAL(KIND=JPRB), INTENT(IN) :: PVO3C(KLON)
    
    TYPE(STACK), INTENT(IN) :: YDSTACK
  END SUBROUTINE SUOZON_OPENACC
END INTERFACE
