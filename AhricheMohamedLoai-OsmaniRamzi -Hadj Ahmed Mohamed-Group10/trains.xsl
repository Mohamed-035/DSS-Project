<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" encoding="UTF-8" indent="yes" />
  
  <!-- Station name lookup template -->
  <xsl:template name="getStationName">
    <xsl:param name="id"/>
    <xsl:value-of select="/transport/stations/station[@id = $id]/@name"/>
  </xsl:template>
  
  <xsl:template match="/">
    <html>
      <head>
        <title>Train Trips Report</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          h1 { text-align: center; color: #003366; }
          h2 { color: #003366; border-bottom: 2px solid #003366; }
          table { border-collapse: collapse; width: 100%; margin: 15px 0; }
          th { background-color: #003366; color: white; padding: 10px; text-align: center; }
          td { border: 1px solid #ddd; padding: 8px; text-align: center; }
          tr:nth-child(even) { background-color: #f2f2f2; }
          .header { text-align: center; font-style: italic; margin-bottom: 30px; }
        </style>
      </head>
      <body>
        <div class="header">
          TP - Do not copy directly / This page is implemented by the student: Ahriche Mohamed loai , Osmani Ramzi , Hadj ahmed Mohamed / Group: 10
        </div>
        <h1>Train Trips Report</h1>
        
        <xsl:for-each select="/transport/lines/line">
          <h2>
            Line: <xsl:value-of select="@code"/> 
            (<xsl:call-template name="getStationName"><xsl:with-param name="id" select="@departure"/></xsl:call-template> 
            → 
            <xsl:call-template name="getStationName"><xsl:with-param name="id" select="@arrival"/></xsl:call-template>)
          </h2>
          
          <h3>Detailed List of Trips:</h3>
          
          <xsl:for-each select="trips/trip">
            <h4>
              Trip No. <xsl:value-of select="@code"/>: 
              departure: <xsl:call-template name="getStationName"><xsl:with-param name="id" select="../../@departure"/></xsl:call-template> | 
              Arrival: <xsl:call-template name="getStationName"><xsl:with-param name="id" select="../../@arrival"/></xsl:call-template>
            </h4>
            
            <table>
              <thead>
                <tr>
                  <th>Schedule</th>
                  <th>Train Type</th>
                  <th>Class</th>
                  <th>Price (DA)</th>
                </tr>
              </thead>
              <tbody>
                <xsl:for-each select="class">
                  <tr>
                    <td>
                      <xsl:value-of select="../schedule/@departure"/> - 
                      <xsl:value-of select="../schedule/@arrival"/>
                    </td>
                    <td><xsl:value-of select="../@type"/></td>
                    <td><xsl:value-of select="@type"/></td>
                    <td><xsl:value-of select="@price"/></td>
                  </tr>
                </xsl:for-each>
              </tbody>
            </table>
          </xsl:for-each>
        </xsl:for-each>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>