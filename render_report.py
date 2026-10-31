"""Render the DOCX with LibreOffice and optionally render every PDF page with Poppler."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--soffice',default='soffice')
    p.add_argument('--poppler',default='')
    p.add_argument('--qa-dir',default='')
    args=p.parse_args();root=Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix='airwatch-lo-') as tmp:
        profile=Path(tmp)/'profile';out=Path(tmp)/'render';out.mkdir()
        cmd=[args.soffice,'--headless',f'-env:UserInstallation={profile.as_uri()}',
             '--convert-to','pdf','--outdir',str(out),str(root/'report/Bengaluru_AirWatch_Final_Report.docx')]
        subprocess.run(cmd,check=True,timeout=240)
        pdf=out/'Bengaluru_AirWatch_Final_Report.pdf'
        if not pdf.exists():raise RuntimeError('LibreOffice did not produce the PDF')
        shutil.copy2(pdf,root/'report'/pdf.name)
    if args.qa_dir:
        qa=Path(args.qa_dir).resolve();qa.mkdir(parents=True,exist_ok=True)
        exe=str(Path(args.poppler)/('pdftoppm.exe' if __import__('os').name=='nt' else 'pdftoppm')) if args.poppler else 'pdftoppm'
        subprocess.run([exe,'-r','110','-png',str(root/'report/Bengaluru_AirWatch_Final_Report.pdf'),str(qa/'page')],check=True,timeout=240)
    print('Rendered report PDF saved in report/.')

if __name__=='__main__':main()
